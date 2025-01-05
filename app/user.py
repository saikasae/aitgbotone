import base64

from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import CommandStart

from app.states import Text
from app.states import Image
from app.states import Code
from app.states import Vision

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


@user.message(Text.wait)
@user.message(Code.wait)
async def fn_wait(message: Message):
    await message.answer(text="Подождите, бот отвечает вам...")


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


@user.message(F.text == 'Генерация изображения')
async def fn_image(message: Message, state: FSMContext):
    await state.set_state(Image.image)
    await message.answer(text='Введите ваш запрос...', reply_markup=kb.main2)

@user.message(Image.image)
async def fn_image_response(message: Message, state: FSMContext):
    try:
        send_message = await message.answer('Бот рисует картину, подождите пару секунд...')
        await state.set_state(Image.wait)

        answer = await image_generation(message.text)
        image_bytes = base64.b64decode(answer)

        await send_message.answer_photo(photo=BufferedInputFile(file=image_bytes, filename='generated_image.jpg'))

        generated_images_dir = 'generated_images'
        if os.path.exists(generated_images_dir):
            for file in os.listdir(generated_images_dir):
                file_path = os.path.join(generated_images_dir, file)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        os.rmdir(generated_images_dir)
                except Exception as e:
                    print(f'Ошибка при удалении файла {file_path}: {str(e)}')
    except Exception as e:
        print('Произошла ошибка:', str(e))
        await message.answer("Произошла ошибка при генерации изображения. Попробуйте еще раз.")
    finally:
        await state.clear()


@user.message(Image.wait)
async def fn_wait(message: Message):
    await message.answer(text='Подождите, бот отвечает вам...')


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


@user.message(F.text == 'Распознавание изображения')
async def fn_vision(message: Message, state: FSMContext):
    await state.set_state(Vision.vision)
    await message.answer(text='Введите ваш запрос...', reply_markup=kb.main2)

@user.message(Vision.vision, F.photo)
async def fn_vision_response(message: Message, state: FSMContext):
    await state.set_state(Vision.wait)

    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    photo_path = f"images/{photo.file_id}.jpg"
    await message.bot.download(file.file_id, destination=photo_path)
    caption = message.caption if message.caption else "Опишите это изображение"

    answer = await image_recognition(photo_path, caption)

    if answer is None:
        await message.answer("Извините, произошла ошибка при обработке изображения. Пожалуйста, попробуйте еще раз.")
    else:
        await message.answer(answer)
    await state.clear()

    os.remove(photo_path)

