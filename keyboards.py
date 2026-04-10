from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import PRODUCTS

def main_menu_kb():
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="🛒 Каталог", callback_data="catalog"))
    b.row(InlineKeyboardButton(text="📦 Мои заказы", callback_data="my_orders"))
    b.row(InlineKeyboardButton(text="ℹ️ Как работает?", callback_data="how_it_works"))
    return b.as_markup()

def catalog_kb():
    b = InlineKeyboardBuilder()
    for pid, p in PRODUCTS.items():
        b.row(InlineKeyboardButton(text=f"{p.emoji} {p.name} — ⭐{p.price_stars}", callback_data=f"product:{pid}"))
    b.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu"))
    return b.as_markup()

def product_kb(product_id):
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="💳 Купить", callback_data=f"buy:{product_id}"))
    b.row(InlineKeyboardButton(text="◀️ Каталог", callback_data="catalog"))
    return b.as_markup()

def confirm_order_kb(order_id):
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="✅ Подтвердить и оплатить", callback_data=f"confirm_pay:{order_id}"))
    b.row(InlineKeyboardButton(text="❌ Отменить", callback_data="catalog"))
    return b.as_markup()
