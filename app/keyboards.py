from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Генерация текста'), KeyboardButton(text='Генерация изображения'), KeyboardButton(text='Генерация кода')],
    [KeyboardButton(text='Распознавание изображения'),]
], resize_keyboard=True)

main2 = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Назад в меню')]], resize_keyboard=True)