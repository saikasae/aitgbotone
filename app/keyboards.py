from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def get_main_keyboard():
    builder = ReplyKeyboardBuilder()

    builder.button(text="Генерация текста")
    builder.button(text="Генерация изображения")
    builder.button(text="Генерация кода")

    builder.button(text="Распознавание изображения")

    builder.button(text="Поиск в Интернете (beta-версия)")

    builder.adjust(3, 1, 1)

    return builder.as_markup(resize_keyboard=True)


def get_main2_keyboard():
    builder = ReplyKeyboardBuilder()

    builder.button(text="Назад в меню")

    return builder.as_markup(resize_keyboard=True)


def get_subs_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text="Перейти в канал", url="https://t.me/+9I7iLTq7vwYzZDIy")
    builder.button(text="✅ Я подписался на канал!", callback_data="subscribe")

    builder.adjust(1)
    return builder.as_markup()
