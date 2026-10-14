# ============================================================
# ui/catalog.py — каталог + карточка товара
# ============================================================
# Каталог: карточки с фильтром/сортировкой/поиском (real-time).
# Скидка 25%, если за прошлый месяц заказов не было.
# Подсветка LowStock.TFrame при остатке ≤ 3.
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox
import database
from config import STATE, setup_window, load_image
from ui.cart import CartWindow


class CatalogWindow:
    def __init__(self, root):
        self.root = root
        setup_window(root, "Каталог")
        root.geometry('900x700')

        # Верхняя панель: ФИО + корзина
        top = ttk.Frame(root); top.pack(fill='x', padx=10, pady=5)
        ttk.Label(top, text=STATE['user']['full_name']).pack(side='right', padx=10)
        ttk.Button(top, text='Корзина', command=self.open_cart).pack(side='right')

        # Фильтры: поиск, категория, сортировка
        filt = ttk.Frame(root); filt.pack(fill='x', padx=10, pady=5)
        self.search = tk.StringVar()
        self.category = tk.StringVar(value='Все категории')
        self.sort = tk.StringVar(value='Без сортировки')

        ttk.Label(filt, text='Поиск:').pack(side='left')
        entry = ttk.Entry(filt, textvariable=self.search)
        entry.pack(side='left', padx=5)
        entry.bind('<KeyRelease>', lambda _: self.load_data())   # real-time

        # Категории из БД, первая — «Все категории» (отключает фильтр)
        try:
            cats = ['Все категории'] + database.fetch_categories()
        except Exception as e:
            messagebox.showerror("Ошибка БД",
                                 "Категории не загружены.\n" + str(e))
            cats = ['Все категории']

        ttk.Label(filt, text='Категория:').pack(side='left', padx=(10, 0))
        cat_cb = ttk.Combobox(filt, textvariable=self.category,
                              state='readonly', values=cats)
        cat_cb.pack(side='left')
        cat_cb.bind('<<ComboboxSelected>>', lambda _: self.load_data())

        ttk.Label(filt, text='Сортировка:').pack(side='left', padx=(10, 0))
        sort_cb = ttk.Combobox(filt, textvariable=self.sort, state='readonly',
                               values=['Без сортировки', 'По возрастанию', 'По убыванию'])
        sort_cb.pack(side='left')
        sort_cb.bind('<<ComboboxSelected>>', lambda _: self.load_data())

        # Прокрутка: Canvas + Frame + Scrollbar
        self.canvas = tk.Canvas(root)
        sb = ttk.Scrollbar(root, command=self.canvas.yview)
        self.frame = ttk.Frame(self.canvas)
        self.frame.bind("<Configure>",
                        lambda _: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        self.canvas.configure(yscrollcommand=sb.set)
        self.canvas.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')
        # Колёсико: Windows + Linux
        self.canvas.bind("<MouseWheel>",
                         lambda e: self.canvas.yview_scroll(int(-e.delta / 120), "units"))
        self.canvas.bind("<Button-4>", lambda _: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind("<Button-5>", lambda _: self.canvas.yview_scroll(1, "units"))

        self.imgs = []       # ссылки на картинки — иначе Tk их удалит
        self.load_data()

    def open_cart(self):
        CartWindow(tk.Toplevel(self.root), self)

    def load_data(self):
        """Перерисовка карточек по текущим фильтрам."""
        for w in self.frame.winfo_children():
            w.destroy()
        self.imgs.clear()

        try:
            prods = database.get_products(
                self.search.get(), self.category.get(), self.sort.get())
        except Exception as e:
            messagebox.showerror("Ошибка загрузки",
                                 "Данные не получены.\n" + str(e))
            return

        for p in prods:
            # Скидка 25%, если за прошлый месяц заказов не было
            price = float(p['price']) * (1.0 if p['has_orders'] else 0.75)

            card = ttk.Frame(self.frame, relief='ridge', borderwidth=2)
            card.pack(fill='x', padx=5, pady=5)
            if p['total_qty'] <= 3:                            # подсветка
                card.configure(style='LowStock.TFrame')

            img = load_image(p['image_path'], card)
            self.imgs.append(img)
            ttk.Label(card, image=img).grid(row=0, column=0, rowspan=4, padx=5)

            # grid: столбцы 0 (фото), 1 (текст), 2 (цена/кнопка)
            ttk.Label(card, text=f"{p['manufacturer']} | {p['product_name']}",
                      font=('TkDefaultFont', 12, 'bold')).grid(row=0, column=1, sticky='w')
            ttk.Label(card, text=f"Категория: {p['category']}").grid(row=1, column=1, sticky='w')
            ttk.Label(card, text=f"Остаток: {p['total_qty']}").grid(row=2, column=1, sticky='w')
            ttk.Label(card, text=f"Состав: {p['composition'] or '—'}").grid(row=3, column=1, sticky='w')
            ttk.Label(card, text=f"Цена: {price:.2f} руб.").grid(row=0, column=2, padx=20)

            # lambda x=p: фиксируем значение на момент создания
            ttk.Button(card, text='Выбрать',
                       command=lambda x=p, pr=price: ProductWindow(
                           tk.Toplevel(self.root), x, pr)
                       ).grid(row=2, column=2)


class ProductWindow:
    """Карточка товара: описание, размер, количество."""

    def __init__(self, root, prod, price):
        self.root = root
        self.prod = prod
        self.price = price
        setup_window(root, prod['product_name'])
        root.geometry('500x420')

        ttk.Label(root, text=STATE['user']['full_name']).pack(anchor='ne', padx=10)
        ttk.Label(root, text=prod['product_name'],
                  font=('TkDefaultFont', 14, 'bold')).pack(pady=5)
        ttk.Label(root, text="Описание: " + (prod['description'] or 'Нет описания'),
                  wraplength=450).pack(pady=5)
        ttk.Label(root, text=f"Цена со скидкой: {price:.2f} руб.",
                  font=('TkDefaultFont', 12)).pack()

        self.sizes = database.get_sizes(prod['product_id'])

        if not self.sizes:
            ttk.Label(root, text="Нет в наличии", foreground="red").pack(pady=10)
        else:
            ttk.Label(root, text="Размер:").pack()
            self.cb = ttk.Combobox(root, state='readonly',
                                   values=[s['size_value'] for s in self.sizes])
            self.cb.pack(); self.cb.current(0)

            ttk.Label(root, text="Количество:").pack()
            self.qty = tk.StringVar(value='1')
            ttk.Spinbox(root, from_=1, to=100, textvariable=self.qty).pack()

            ttk.Button(root, text="В корзину", command=self.add).pack(pady=10)

        ttk.Button(root, text="Назад", command=root.destroy).pack()

    def add(self):
        """Валидация ввода и добавление в STATE['cart']."""
        try:
            qty_str = self.qty.get()
            if not qty_str.isdigit():
                raise ValueError("Количество должно быть целым числом.")
            qty = int(qty_str)
            if qty <= 0:
                raise ValueError("Количество должно быть больше нуля.")

            # Поиск выбранного размера в списке
            size_val = self.cb.get()
            size_data = next((s for s in self.sizes
                              if str(s['size_value']) == size_val), None)
            if size_data is None:
                raise ValueError("Размер не найден.")

            # Проверка остатка
            if qty > size_data['quantity_available']:
                messagebox.showwarning(
                    "Превышение остатка",
                    f"Указано {qty} шт., доступно только "
                    f"{size_data['quantity_available']}.\n"
                    "Укажите меньшее количество.")
                return

            STATE['cart'].append({
                'product_id':   self.prod['product_id'],
                'product_name': self.prod['product_name'],
                'size_id':      size_data['size_id'],
                'size_value':   size_val,
                'qty':          qty,
                'price':        self.price
            })
            messagebox.showinfo("Успех", "Позиция добавлена в корзину.")
            self.root.destroy()

        except ValueError as ve:
            messagebox.showerror("Некорректный ввод",
                                 f"Ошибка: {ve}\n"
                                 "Введите целое положительное число.")
        except Exception as e:
            messagebox.showerror("Непредвиденная ошибка",
                                 f"Не удалось добавить.\n{e}")