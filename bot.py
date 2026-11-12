import asyncio
import logging
import os
import socket
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.client.session.aiohttp import AiohttpSession
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Подключаемся к SQL-базе
engine = create_engine("sqlite:///warehouse_db.sqlite")
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    stock = Column(Integer, default=0)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Описываем шаги диалога (Машина состояний FSM)
class AddProduct(StatesGroup):
    name = State()   # Шаг 1: ждем название
    price = State()  # Шаг 2: ждем цену
    stock = State()  # Шаг 3: ждем остаток

# Настройка бота с принудительным IPv4
net_session = AiohttpSession()
net_session._connector_init["family"] = socket.AF_INET

bot = Bot(token=TOKEN, session=net_session)
dp = Dispatcher()

# Нижнее меню теперь с двумя кнопками
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📦 Управление складом")],
        [KeyboardButton(text="➕ Добавить новый товар")],
        [KeyboardButton(text="💰 Бюджет склада")],
        [KeyboardButton(text="🚨 Список на закупку")]
    ],
    resize_keyboard=True
)

def build_warehouse_panel():
    db = Session()
    products = db.query(Product).all()
    db.close()

    if not products:
        return "Склад пока пуст!", None

    text = "📊 Панель управления складом (SQL):\nНажимай на кнопки ниже для продажи или приемки:\n\n"
    inline_buttons = []

    for item in products:
        text += f"🔹 {item.name} — {item.stock} шт. (по {item.price} руб.)\n"
        row = [
            InlineKeyboardButton(text=f"➖1 {item.name}", callback_data=f"sell_{item.id}"),
            InlineKeyboardButton(text=f"➕5 {item.name}", callback_data=f"add_{item.id}")
        ]
        inline_buttons.append(row)

    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_buttons)
    return text, keyboard

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()  # Сбрасываем незавершенные диалоги, если они были
    await message.answer(
        f"Привет, {message.from_user.first_name}! Выбери действие в меню ниже:",
        reply_markup=main_menu
    )

@dp.message(F.text == "📦 Управление складом")
async def show_warehouse(message: types.Message):
    text, keyboard = build_warehouse_panel()
    await message.answer(text, reply_markup=keyboard)

@dp.message(F.text == "💰 Бюджет склада")
async def calc_budget(message:types.Message):
    db = Session()
    products = db.query(Product).all()
    db.close()
    total_sum = 0
    for item in products:
        total_sum += item.price * item.stock
    await message.answer(
            f"Общий бюджет склада составляет {total_sum} руб.")

@dp.message(F.text =="🚨 Список на закупку")
async def check_low_stock(message:types.Message):
    db = Session()
    low_product = db.query(Product).filter(Product.stock <=5).all()
    db.close()
    if not low_product:
        await message.answer ("✅ На складе всего достаточно, закупка не требуется!")
        return
    report = "🚨 Нужно срочно докупить:\n\n"
    for item in low_product:
        report += f"{item.name} - осталось {item.stock} шт.\n"
    await message.answer(report)

# --- НАЧАЛО ДИАЛОГА ДОБАВЛЕНИЯ ТОВАРА (FSM) ---

# Шаг 1: Пользователь нажал кнопку "➕ Добавить новый товар"
@dp.message(F.text == "➕ Добавить новый товар")
async def start_add_product(message: types.Message, state: FSMContext):
    await state.set_state(AddProduct.name)
    await message.answer("✍️ Введи название нового табака (например: Musthave Pinkman):")

# Шаг 2: Ловим название и спрашиваем цену
@dp.message(AddProduct.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddProduct.price)
    await message.answer("💰 Отлично! Теперь введи цену за пачку (только число, например: 1450):")

# Шаг 3: Ловим цену (с проверкой, что введено число) и спрашиваем остаток
@dp.message(AddProduct.price)
async def process_price(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Цена должна быть числом! Введи цену цифрами:")
        return

    await state.update_data(price=int(message.text))
    await state.set_state(AddProduct.stock)
    await message.answer("📦 Сколько пачек сейчас приехало на склад? (введи число):")

# Шаг 4: Ловим остаток, сохраняем товар в SQL и показываем обновленный склад
@dp.message(AddProduct.stock)
async def process_stock(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Количество должно быть числом! Введи остаток цифрами:")
        return

    data = await state.get_data()  # Достаем сохраненные имя и цену из памяти FSM
    product_name = data["name"]
    product_price = data["price"]
    product_stock = int(message.text)

    # Записываем новый товар в базу данных SQLite
    db = Session()
    new_item = Product(name=product_name, price=product_price, stock=product_stock)
    db.add(new_item)
    db.commit()
    db.close()

    await state.clear()  # Выключаем режим опроса

    await message.answer(
        f"✅ Товар «{product_name}» ({product_stock} шт. по {product_price} руб.) успешно записан в SQL-базу!"
    )

    # Сразу показываем панель со свежими Inline-кнопками
    text, keyboard = build_warehouse_panel()
    await message.answer(text, reply_markup=keyboard)

# --- ОБРАБОТКА INLINE-КНОПОК (+5 и -1) ---

@dp.callback_query(F.data.startswith(("sell_", "add_")))
async def process_stock_change(callback: types.CallbackQuery):
    action, product_id_str = callback.data.split("_")
    product_id = int(product_id_str)

    db = Session()
    product = db.query(Product).filter_by(id=product_id).first()

    if not product:
        db.close()
        await callback.answer("Товар не найден в базе!", show_alert=True)
        return

    if action == "sell":
        if product.stock == 0:
            db.close()
            await callback.answer(f"❌ Ошибка! {product.name} закончился на складе!", show_alert=True)
            return
        product.stock = product.stock - 1
        notice = f"🛒 Продано: {product.name} (1 шт.)"
    elif action == "add":
        product.stock = product.stock + 5
        notice = f"✅ Принята поставка: {product.name} (+5 шт.)"

    db.commit()
    db.close()

    new_text, new_keyboard = build_warehouse_panel()
    await callback.message.edit_text(new_text, reply_markup=new_keyboard)
    await callback.answer(notice)

async def main():
    logging.basicConfig(level=logging.INFO)
    print("=== Бот с FSM запущен! Открой Telegram и нажми /start ===")
    await dp.start_polling(bot)

asyncio.run(main())