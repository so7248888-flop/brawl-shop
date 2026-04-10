from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import re

from config import PRODUCTS, ADMIN_IDS
from database import create_order, update_order_supercell_id, get_order, mark_order_paid, mark_order_completed
from keyboards import main_menu_kb, catalog_kb, product_kb, confirm_order_kb
from fulfillment import fulfill_order

router = Router()

class OrderStates(StatesGroup):
    waiting_supercell_id = State()

SC_PATTERN = re.compile(r"^#?[0289PYLQGRJCUV]{6,12}$", re.IGNORECASE)

@router.message(CommandStart())
async def start(message: Message):
    text = "🎮 <b>Добро пожаловать в Brawl Stars Shop!</b>\n\nОплата ⭐ Telegram Stars\nПосле оплаты укажи Supercell ID"
    await message.answer(text, reply_markup=main_menu_kb())

@router.callback_query(F.data == "catalog")
async def show_catalog(callback: CallbackQuery):
    await callback.message.edit_text("🛒 <b>Выбери товар:</b>", reply_markup=catalog_kb())

@router.callback_query(F.data.startswith("product:"))
async def show_product(callback: CallbackQuery):
    product_id = callback.data.split(":")[1]
    product = PRODUCTS.get(product_id)
    if not product:
        return await callback.answer("Товар не найден")
    text = f"{product.emoji} <b>{product.name}</b>\n\n{product.description}\n\nЦена: ⭐ {product.price_stars} Stars"
    await callback.message.edit_text(text, reply_markup=product_kb(product_id))

@router.callback_query(F.data.startswith("buy:"))
async def buy_product(callback: CallbackQuery, state: FSMContext):
    product_id = callback.data.split(":")[1]
    product = PRODUCTS[product_id]

    order_id = await create_order(
        callback.from_user.id,
        callback.from_user.username,
        product.id,
        product.name,
        product.price_stars
    )

    await state.set_state(OrderStates.waiting_supercell_id)
    await state.update_data(order_id=order_id, product_id=product_id)

    await callback.message.edit_text(
        f"📝 Заказ #{order_id}\nТовар: {product.emoji} {product.name}\n\nВведи свой <b>Supercell ID</b> (например #2Y8RLLVQJ)"
    )

@router.message(StateFilter(OrderStates.waiting_supercell_id))
async def get_sc_id(message: Message, state: FSMContext):
    sc_id = message.text.strip().upper()
    if not sc_id.startswith("#"):
        sc_id = "#" + sc_id

    if not SC_PATTERN.match(sc_id):
        return await message.answer("❌ Неверный Supercell ID. Попробуй ещё раз.")

    data = await state.get_data()
    await update_order_supercell_id(data["order_id"], sc_id)
    await state.clear()

    product = PRODUCTS[data["product_id"]]
    await message.answer(
        f"✅ Проверь заказ:\n\nТовар: {product.emoji} {product.name}\nЦена: ⭐ {product.price_stars}\nID: <code>{sc_id}</code>",
        reply_markup=confirm_order_kb(data["order_id"])
    )

@router.callback_query(F.data.startswith("confirm_pay:"))
async def send_payment(callback: CallbackQuery, bot):
    order_id = int(callback.data.split(":")[1])
    order = await get_order(order_id)
    product = PRODUCTS[order["product_id"]]

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title=f"{product.emoji} {product.name}",
        description=f"Supercell ID: {order['supercell_id']}",
        payload=f"order:{order_id}",
        currency="XTR",
        prices=[{"label": product.name, "amount": product.price_stars}]
    )

@router.pre_checkout_query()
async def pre_checkout(pre_checkout, bot):
    await bot.answer_pre_checkout_query(pre_checkout.id, ok=True)

@router.message(F.successful_payment)
async def payment_success(message: Message, bot):
    payload = message.successful_payment.invoice_payload
    order_id = int(payload.split(":")[1])

    await mark_order_paid(order_id, message.successful_payment.telegram_payment_charge_id, "")

    order = await get_order(order_id)
    await message.answer("✅ Оплата прошла! Выполняем заказ...")

    success = await fulfill_order(order)
    if success:
        await mark_order_completed(order_id)
        await message.answer("🎉 Заказ выполнен!")
    else:
        await message.answer("⏳ Заказ отправлен администратору на ручную обработку (до 30 мин)")
