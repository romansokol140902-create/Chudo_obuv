# Чудо Обувь — приложение для заказа обуви (Модули 1–3)

## Технологии
- Python 3.10+ (Tkinter)
- MySQL 8 (mysql-connector-python)
- Pillow (обработка изображений)

## Установка
    pip install mysql-connector-python pillow
                    или
    py -m pip install mysql-connector-python pillow
1. Выполните init_db.sql в MySQL.
2. Настройте DB_CONFIG в config.py (пароль root).
3. Запустите: python main.py

## Логины (пароль не требуется)
- ivanov  — user (каталог + корзина)
- petrov  — manager
- sidorov — admin

## Функционал
- Авторизация по логину, без пароля
- Каталог с фильтром, сортировкой и поиском в реальном времени
- Скидка 25% на товары без заказов за предыдущий календарный месяц
- Подсветка товаров с остатком ≤ 3
- Карточка товара: описание, выбор размера и количества
- Корзина: изменение количества, удаление, оформление заказа
- Оформление заказа одной транзакцией (INSERT + UPDATE + COMMIT)


auth_user	коннект → SELECT с JOIN → fetchone → finally close
get_products	2 границы месяца → SELECT с EXISTS → фильтры → fetchall
create_order	INSERT orders → lastrowid → for cart: INSERT + UPDATE → commit/rollback
load_data	очистка → get_products → for: карточка со скидкой и подсветкой
add	валидация → проверка остатка → append в STATE['cart']
checkout	проверка → askyesno → create_order → clear → parent.load_data
