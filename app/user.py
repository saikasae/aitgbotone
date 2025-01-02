from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from app.states import Text

"""
from app.states import Image
"""
from app.states import Code

"""
from app.states import Vision
"""
from aiogram.fsm.context import FSMContext
from app.generators import text_generation
from app.generators import image_generation
from app.generators import code_generation
from app.generators import image_recognition
from app.database.requests import set_user
import app.keyboards as kb
import uuid
import os

user = Router()


@user.message(CommandStart())
async def cmnd_start(message: Message, state: FSMContext):
    await set_user(message.from_user.id)
    await message.answer(text="Добро пожаловать!", reply_markup=kb.main)
    await state.clear()


@user.message(F.text == "Назад в меню")
async def cmnd_close(message: Message, state: FSMContext):
    await set_user(message.from_user.id)
    await message.answer(text="Вы вернулись в меню!", reply_markup=kb.main)
    await state.clear()


@user.message(F.text == "Генерация текста")
async def fn_text(message: Message, state: FSMContext):
    await state.set_state(Text.text)
    await message.answer(text="Введите ваш запрос...", reply_markup=kb.main2)


@user.message(Text.text)
async def fn_text_response(message: Message, state: FSMContext):
    await state.set_state(Text.wait)
    res = await text_generation(message.text)
    await message.answer(res)
    await state.set_state(Text.text)


@user.message(Text.wait)
@user.message(Code.wait)
async def fn_wait(message: Message):
    await message.answer(text="Подождите, бот отвечает вам...")


"""
@user.message(F.text == 'Генерация изображения')
async def fn_image(message: Message, state: FSMContext):
    await state.set_state(Image.image)
    await message.answer(text='Введите ваш запрос...', reply_markup=kb.main2)

@user.message(...)
async def fn_image_response(message: Message, state: FSMContext):
    ...

@user.message(Image.wait)
async def fn_wait(message: Message):
    await message.answer(text='Подождите, бот отвечает вам...')
"""


@user.message(F.text == "Генерация кода")
async def fn_code(message: Message, state: FSMContext):
    await state.set_state(Code.code)
    await message.answer(text="Введите ваш запрос...", reply_markup=kb.main2)


@user.message(Code.code)
async def fn_code_response(message: Message, state: FSMContext):
    await state.set_state(Code.wait)
    res = await code_generation(message.text)
    await message.answer(res)
    await state.set_state(Code.code)


"""
@user.message(F.text == 'Распознавание изображения')
async def fn_vision(message: Message, state: FSMContext):
    await state.set_state(Vision.vision)
    await message.answer(text='Введите ваш запрос...', reply_markup=kb.main2)

@user.message(Vision.vision, F.photo)
async def fn_vision_response(message: Message, state: FSMContext):
    await state.set_state(Vision.wait)
    file = await message.bot.get_file(message.photo[-1].file_id)
    file_path = file.file_path
    file_name = uuid.uuid4()
    await message.bot.dowload_file(file_path, f'{file_name}.jpeg')
    res = await image.recognition(message.caption, f'{file_name}.jpeg')
    await message.answer(res)
    await state.set_state(Vision.vision)
    os.remove(f'{file_name}.jpeg')

@user.message(Vision.wait)
async def fn_wait(message: Message):
    await message.answer(text='Подождите, бот отвечает вам...')
"""
