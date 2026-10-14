# ============================================================
# ui/cart.py — корзина: список позиций + оформление заказа
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import database
from config import STATE, setup_window


class CartWindow:
    def __init__(self, root, parent):
        self.root = root
        self.parent = parent         # ссылка на каталог — для обновления после заказа
        setup_window(root, "Корзина")
        root.geometry('600x400')

        ttk.Label(root, text="Пользователь: " + STATE['user']['full_name']
                  ).pack(anchor='ne', padx=10, pady=5)

        # Таблица позиций
        self.tree = ttk.Treeview(root, columns=('name', 'size', 'qty', 'price'),
                                 show='headings')
        for col, text in zip(self.tree['columns'],
                             ['Товар', 'Размер', 'Кол-во', 'Цена']):
            self.tree.heading(col, text=text)
        self.tree.pack(fill='both', expand=True, padx=10)
        self.tree.bind('<Double-1>', lambda _: self.edit_qty())

        # Кнопки
        btns = ttk.Frame(root)
        btns.pack(pady=10)
        ttk.Button(btns, text="Изменить",
                   command=self.edit_qty).pack(side='left', padx=5)
        ttk.Button(btns, text="Удалить",
                   command=self.remove).pack(side='left', padx=5)
        ttk.Button(btns, text="Оформить заказ",
                   command=self.checkout).pack(side='left', padx=5)

        self.refresh()

    def refresh(self):
        """Перерисовка таблицы из STATE['cart']."""
        for row in self.tree.get_children():
            self.tree.delete(row)
        for i, item in enumerate(STATE['cart']):
            # iid=str(i): ID строки = индекс в списке корзины
            self.tree.insert('', 'end', iid=str(i),
                             values=(item['product_name'], item['size_value'],
                                     item['qty'], f"{item['price']:.2f}"))

    def edit_qty(self):
        """Изменение количества выбранной позиции."""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Отмена", "Выделите товар в списке.")
            return
        idx = int(sel[0])
        item = STATE['cart'][idx]
        # askinteger даёт встроенную валидацию (min/max). None при отмене.
        new_qty = simpledialog.askinteger("Изменение количества",
                                          "Введите новое количество пар:",
                                          initialvalue=item['qty'],
                                          minvalue=1, maxvalue=999)
        if new_qty is None:
            return
        item['qty'] = new_qty
        self.refresh()

    def remove(self):
        """Удаление выделенной позиции."""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Отмена", "Сначала выделите товар.")
            return
        del STATE['cart'][int(sel[0])]
        self.refresh()

    def checkout(self):
        """Оформление заказа: транзакция в БД."""
        # Проверка пустой корзины — до подтверждения
        if not STATE['cart']:
            messagebox.showwarning("Пустая корзина",
                                   "Добавьте товары перед оформлением.")
            return
        # Подтверждение необратимой операции (КИМ 3.2)
        if not messagebox.askyesno("Подтверждение",
                                   "Оформить заказ и списать товар со склада?"):
            return
        try:
            oid = database.create_order(STATE['user']['user_id'], STATE['cart'])
            STATE['cart'].clear()        # in-place — ссылки остаются валидны
            messagebox.showinfo("Готово",
                                "Заказ №" + str(oid) + " сохранён.\n"
                                "Товары зарезервированы на складе.")
            self.parent.load_data()      # обновить каталог
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка оформления",
                                 "Не удалось создать заказ.\n" + str(e))