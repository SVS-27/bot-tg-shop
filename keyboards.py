from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Reply-клавиатура (главное меню)
button_catalog = KeyboardButton(text="🛍 Каталог")
button_cart = KeyboardButton(text="🛒 Корзина")

main_menu = ReplyKeyboardMarkup(
    keyboard=[[button_catalog, button_cart]],  # Размещаем кнопки в одном ряду
    resize_keyboard=True
)

# Inline-клавиатура (встроенные кнопки в сообщении)
button_view_products = InlineKeyboardButton(
    text="📦 Смотреть товары",
    callback_data="view_products"
)

catalog_keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_view_products]])