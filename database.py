# ============================================================
# database.py — весь SQL приложения
# ============================================================
# Все запросы используют %s (защита от инъекций).
# Соединения закрываются в finally — не текут.
# create_order работает в транзакции.
# ============================================================

import mysql.connector
from datetime import datetime, timedelta
from config import DB_CONFIG


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def auth_user(login):
    """Поиск пользователя по логину с ролью."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT u.user_id, u.last_name, u.first_name, u.middle_name, r.role_name
            FROM users u JOIN roles r ON u.role_id = r.role_id
            WHERE u.login = %s
        """, (login,))
        return cur.fetchone()
    finally:
        cur.close(); conn.close()


def get_products(search='', category='Все категории', sort_order=''):
    """Товары + сумма остатков + флаг заказов за прошлый месяц."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        # Границы предыдущего календарного месяца (для скидки 25%)
        now = datetime.now()
        first_prev = (now.replace(day=1) - timedelta(days=1)).replace(day=1)
        last_prev = now.replace(day=1) - timedelta(days=1)

        query = """
            SELECT p.*, COALESCE(SUM(si.quantity_available), 0) AS total_qty,
                   EXISTS (SELECT 1 FROM order_items oi
                           JOIN orders o ON oi.order_id = o.order_id
                           WHERE oi.product_id = p.product_id
                             AND o.order_date BETWEEN %s AND %s) AS has_orders
            FROM products p LEFT JOIN stock_items si ON p.product_id = si.product_id
            WHERE 1=1
        """
        params = [first_prev, last_prev]

        # Поиск без учёта регистра по имени и описанию
        if search:
            query += " AND (LOWER(p.product_name) LIKE %s OR LOWER(COALESCE(p.description,'')) LIKE %s)"
            params += [f"%{search.lower()}%", f"%{search.lower()}%"]
        # Фильтр по категории («Все категории» отключает фильтр)
        if category != 'Все категории':
            query += " AND p.category = %s"
            params.append(category)

        query += " GROUP BY p.product_id"

        if sort_order == 'По возрастанию':
            query += " ORDER BY p.price ASC"
        elif sort_order == 'По убыванию':
            query += " ORDER BY p.price DESC"

        cur.execute(query, params)
        return cur.fetchall()
    finally:
        cur.close(); conn.close()


def fetch_categories():
    """Уникальные категории для выпадающего фильтра."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT DISTINCT category FROM products ORDER BY category")
        return [r[0] for r in cur.fetchall()]
    finally:
        cur.close(); conn.close()


def get_sizes(prod_id):
    """Размеры товара, которых на складе > 0."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT si.size_id, s.size_value, si.quantity_available
            FROM stock_items si JOIN sizes s ON si.size_id = s.size_id
            WHERE si.product_id = %s AND si.quantity_available > 0
        """, (prod_id,))
        return cur.fetchall()
    finally:
        cur.close(); conn.close()


def create_order(user_id, cart):
    """Создание заказа + списание со склада в одной транзакции."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Шаг 1: сам заказ
        cur.execute("INSERT INTO orders (order_date, user_id) VALUES (%s, %s)",
                    (datetime.now().date(), user_id))
        oid = cur.lastrowid

        # Шаг 2: позиции + уменьшение остатков
        for item in cart:
            cur.execute("""
                INSERT INTO order_items (order_id, product_id, size_id, quantity, price)
                VALUES (%s, %s, %s, %s, %s)
            """, (oid, item['product_id'], item['size_id'], item['qty'], item['price']))
            cur.execute("""
                UPDATE stock_items SET quantity_available = quantity_available - %s
                WHERE product_id = %s AND size_id = %s
            """, (item['qty'], item['product_id'], item['size_id']))

        conn.commit()
        return oid
    except Exception:
        conn.rollback()   # откат при любой ошибке
        raise
    finally:
        cur.close(); conn.close()