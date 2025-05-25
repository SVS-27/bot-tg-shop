from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from keyboards import main_menu
from database import get_products, add_to_cart, get_cart, create_order, remove_from_cart

router = Router()

# Обработчик команды /start
@router.message(F.text == "/start")
async def start_command(message: Message):
    await message.answer("Добро пожаловать в магазин! Выберите действие:", reply_markup=main_menu)

# Обработчик кнопки "Каталог"
@router.message(F.text == "🛍 Каталог")
async def catalog_command(message: Message):
    await message.answer("Вот наш каталог. Выберите товар и укажите его количество:")

    products = get_products()
    for product in products:
        product_id, name, price = product
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить", callback_data=f"add_{product_id}")],
            [InlineKeyboardButton(text="➖ Убрать", callback_data=f"remove_{product_id}")]
        ])
        await message.answer(f"{name} - {price}₽", reply_markup=keyboard)

# Обработчик кнопок "Добавить" и "Удалить"
@router.callback_query(F.data.startswith("add_") | F.data.startswith("remove_"))
async def update_cart_handler(callback: CallbackQuery):
    action, product_id = callback.data.split("_")
    product_id = int(product_id)

    if action == "add":
        add_to_cart(callback.from_user.id, product_id)
        await callback.answer("✅ Товар добавлен!")
    elif action == "remove":
        remove_from_cart(callback.from_user.id, product_id)
        await callback.answer("❌ Товар убран!")

# Обработчик кнопки "Корзина" и "🔄 Обновить корзину"
@router.message(F.text == "🛒 Корзина")
@router.callback_query(F.data == "refresh_cart")  # Теперь корзину можно обновлять кнопкой
async def cart_command(event):
    user_id = event.from_user.id if isinstance(event, CallbackQuery) else event.from_user.id
    chat_id = event.message.chat.id if isinstance(event, CallbackQuery) else event.chat.id

    cart_items = get_cart(user_id)

    if not cart_items:
        await event.message.answer("Ваша корзина пуста.")
    else:
        cart_text = "🛒 Ваша корзина:\n"
        total_price = 0
        keyboard_buttons = []

        for name, quantity, price, product_id in cart_items:
            total_price += quantity * price
            cart_text += f"{name} — {quantity} шт. × {price}₽ = {quantity * price}₽\n"

            keyboard_buttons.append([
                InlineKeyboardButton(text="➕", callback_data=f"add_{product_id}"),
                InlineKeyboardButton(text="➖", callback_data=f"remove_{product_id}")
            ])

        cart_text += f"\n💰 Итоговая сумма: {total_price}₽"

        # Добавляем кнопку "🔄 Обновить корзину" и "✅ Оформить заказ"
        keyboard_buttons.append([
            InlineKeyboardButton(text="🔄 Обновить корзину", callback_data="refresh_cart")
        ])
        keyboard_buttons.append([
            InlineKeyboardButton(text="✅ Оформить заказ", callback_data="checkout")
        ])

        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

        if isinstance(event, CallbackQuery):  # Если обновление через кнопку
            await event.message.edit_text(cart_text, reply_markup=keyboard)
            await event.answer()
        else:  # Если обычный текст "Корзина"
            await event.answer(cart_text, reply_markup=keyboard)

# Обработчик кнопки "Оформить заказ"
@router.callback_query(F.data == "checkout")
async def request_contact(callback: CallbackQuery):
    contact_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Отправить номер", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await callback.message.answer("📱 Отправьте свой номер телефона для оформления заказа:", reply_markup=contact_keyboard)
    await callback.answer()

# Обработчик получения номера телефона
@router.message(F.contact | F.text.regexp(r'^\+?\d{10,15}$'))
async def receive_contact(message: Message):
    phone_number = message.contact.phone_number if message.contact else message.text
    order_id = create_order(message.from_user.id)

    if order_id:
        await message.answer(f"✅ Заказ #{order_id} оформлен!\n📞 Мы свяжемся с вами по номеру: {phone_number}.")
    else:
        await message.answer("❌ Ваша корзина пуста, добавьте товары перед заказом.")