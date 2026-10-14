# ============================================================
# main.py — точка входа: окно авторизации
# ============================================================
# После успешного логина окно закрывается, открывается каталог.
# Тема 'clam' нужна для корректной подсветки LowStock на Linux.
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox
import database
from config import STATE, setup_window


def login(root, entry):
    """
    Проверяет логин и открывает каталог.
    Вход в систему — только по логину, без пароля (требование КИМ).
    """
    # .strip() — убираем случайные пробелы по краям
    login_val = entry.get().strip()

    # 1. Пустой логин — предупреждение
    if not login_val:
        messagebox.showwarning("Пустой ввод", "Введите логин для входа.")
        return

    # 2. Запрос к БД (может упасть, если MySQL недоступен)
    try:
        user = database.auth_user(login_val)
    except Exception as e:
        messagebox.showerror("Ошибка соединения",
                             "Нет связи с MySQL.\nПроверьте сервер и config.py.\n" + str(e))
        return

    # 3. Логина нет в системе — отказ
    if not user:
        messagebox.showerror("Отказано в доступе",
                             "Пользователя с таким логином не существует.\n"
                             "Используйте логин из списка пользователей системы.")
        return

    # 4. Успех: сохраняем в глобальную сессию и переходим к каталогу
    STATE['user'] = {
        'user_id':   user['user_id'],
        'full_name': user['last_name'] + ' ' + user['first_name'],
        'role_name': user['role_name']
    }

    # Закрываем окно логина и создаём главное окно каталога.
    # ВАЖНО: новый tk.Tk() без .mainloop() не запустится — вызываем его явно.
    root.destroy()
    from ui.catalog import CatalogWindow      # локальный импорт — избегаем циклов
    catalog_root = tk.Tk()
    CatalogWindow(catalog_root)
    catalog_root.mainloop()


# ============================================================
# Точка входа приложения
# ============================================================
if __name__ == '__main__':
    root = tk.Tk()

    # ---------- Тема ttk ----------
    # 'clam' — кроссплатформенная тема, уважает background у ttk.Frame.
    # Без неё подсветка LowStock.TFrame на Linux/macOS не сработает.
    style = ttk.Style()
    try:
        style.theme_use('clam')
    except tk.TclError:
        pass    # если темы нет (редкий случай) — просто пропускаем

    # Регистрируем свой стиль для подсветки товаров с остатком ≤ 3.
    # Применяется в catalog.py через card.configure(style='LowStock.TFrame').
    style.configure('LowStock.TFrame', background='#ffcccc')

    setup_window(root, "Авторизация")
    root.geometry('300x150')

    # ---------- Виджеты окна логина ----------
    ttk.Label(root, text="Вход в Чудо Обувь",
              font=('TkDefaultFont', 14)).pack(pady=10)
    ttk.Label(root, text="Логин:").pack()

    entry = ttk.Entry(root)
    entry.pack(pady=5)

    # lambda — иначе функция вызвалась бы сразу при создании кнопки
    ttk.Button(root, text="Войти",
               command=lambda: login(root, entry)).pack(pady=10)

    root.mainloop()