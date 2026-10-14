# ============================================================
# config.py — настройки и общие утилиты
# ============================================================
# Здесь лежит:
#   1. Параметры подключения к MySQL
#   2. Глобальное состояние сессии (STATE) — кто вошёл и что в корзине
#   3. Хелпер setup_window — единый заголовок и иконка окна
#   4. Хелпер load_image — загрузка картинки товара с заглушками
# ============================================================

import tkinter as tk
import os
from PIL import Image, ImageTk


# ---------- Параметры подключения к базе данных ----------
# Словарь распаковывается в mysql.connector.connect(**DB_CONFIG)
# host='127.0.0.1' — локальный сервер. Не 'localhost', чтобы избежать
# проблем с unix-socket на Linux.
DB_CONFIG = {
    'host':     '127.0.0.1',
    'user':     'root',
    'password': 'root',
    'database': 'chudo_obuv'
}


# ---------- Глобальное состояние сессии ----------
# Единственный мутабельный объект на всё приложение.
# 'user' — словарь {'user_id', 'full_name', 'role_name'} после логина.
# 'cart' — список позиций корзины, каждая позиция тоже словарь.
STATE = {
    'user': None,
    'cart': []
}


def setup_window(window, title):
    """
    Единая настройка окна:
      - заголовок формата "<title> - Чудо Обувь"
      - иконка из icon.png (если файла нет — молча пропускаем)
    """
    window.title(f"{title} - Чудо Обувь")

    # Иконка: обёрнута в try, потому что PhotoImage падает,
    # если файл не найден или не является картинкой.
    try:
        window.iconphoto(False, tk.PhotoImage(file='icon.png'))
    except Exception:
        pass


def load_image(path, master, size=(120, 120)):
    """
    Загрузка изображения товара с двойной защитой:
      1. Если путь пустой или файла нет — берём picture.png (заглушка).
      2. Если и заглушку открыть не удалось — возвращаем серый прямоугольник.

    master — родительский виджет для PhotoImage, иначе Tk может потерять картинку.
    """
    # Проверка 1: путь не указан или файл физически отсутствует
    if not path or not os.path.exists(path):
        path = 'picture.png'

    try:
        # Открываем, конвертируем в RGB (некоторые PNG — RGBA, несовместимы с Tk),
        # масштабируем до size с качественной интерполяцией LANCZOS
        img = Image.open(path).convert('RGB').resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img, master=master)
    except Exception:
        # Проверка 2: даже picture.png не открылся — отдаём серую заглушку
        return ImageTk.PhotoImage(Image.new('RGB', size, color='#ccc'), master=master)