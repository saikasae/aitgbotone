from aiogram import Router, F
from datetime import datetime, timedelta
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import CommandStart
from app.states import Text
from app.states import Image
from app.states import Code
from app.states import Vision
from app.states import Internet
from aiogram.fsm.context import FSMContext
from app.generators import text_generation
from app.generators import image_generation
from app.generators import code_generation
from app.generators import image_recognition
from app.generators import search_with_mistral
from app.database.requests import set_user
import app.keyboards as kb
import os
import base64
import asyncio

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
@user.message(Image.wait)
@user.message(Code.wait)
@user.message(Vision.wait)
@user.message(Internet.wait)
async def fn_wait(message: Message):
    await message.answer(text="Подождите, бот отвечает вам...")


@user.message(F.text == "Генерация текста")
async def fn_text(message: Message, state: FSMContext):
    await state.set_state(Text.text)
    await message.answer(text="Введите ваш запрос...", reply_markup=kb.main2)


@user.message(Text.text)
async def fn_text_response(message: Message, state: FSMContext):
    current_time = datetime.now()
    data = await state.get_data()
    last_request_time = data.get("last_request_time")
    if last_request_time:
        last_request_time = datetime.fromisoformat(last_request_time)
        if current_time - last_request_time < timedelta(seconds=15):
            remaining_time = 15 - (current_time - last_request_time).total_seconds()
            await message.answer(
                f"Подождите ещё {int(remaining_time)} секунд перед следующим запросом"
            )
            return
    await message.answer("Бот генерирует ответ, подождите пару секунд...")
    await state.set_state(Text.wait)
    res = await text_generation(message.text)
    await message.answer(res)
    await state.update_data(last_request_time=current_time.isoformat())
    await state.set_state(Text.text)


@user.message(F.text == "Генерация изображения")
async def fn_image(message: Message, state: FSMContext):
    await state.set_state(Image.image)
    await message.answer(text="Введите ваш запрос...", reply_markup=kb.main2)


@user.message(Image.image)
async def fn_image_response(message: Message, state: FSMContext):
    current_time = datetime.now()
    data = await state.get_data()
    last_request_time = data.get("last_request_time")
    if last_request_time:
        last_request_time = datetime.fromisoformat(last_request_time)
        if current_time - last_request_time < timedelta(seconds=15):
            remaining_time = 15 - (current_time - last_request_time).total_seconds()
            await message.answer(
                f"Подождите ещё {int(remaining_time)} секунд перед следующим запросом"
            )
            return
    send_message = await message.answer(
        "Бот генерирует ответ, подождите пару секунд..."
    )
    await state.set_state(Image.wait)
    answer = await image_generation(message.text)
    image_bytes = base64.b64decode(answer)
    await send_message.answer_photo(
        photo=BufferedInputFile(file=image_bytes, filename="generated_image.jpg")
    )
    generated_images_dir = "generated_images"
    if os.path.exists(generated_images_dir):
        for file in os.listdir(generated_images_dir):
            file_path = os.path.join(generated_images_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
                os.rmdir(generated_images_dir)
    await state.update_data(last_request_time=current_time.isoformat())
    await state.set_state(Image.image)


@user.message(F.text == "Генерация кода")
async def fn_code(message: Message, state: FSMContext):
    await state.set_state(Code.code)
    await message.answer(text="Введите ваш запрос...", reply_markup=kb.main2)


@user.message(Code.code)
async def fn_code_response(message: Message, state: FSMContext):
    current_time = datetime.now()
    data = await state.get_data()
    last_request_time = data.get("last_request_time")
    if last_request_time:
        last_request_time = datetime.fromisoformat(last_request_time)
        if current_time - last_request_time < timedelta(seconds=15):
            remaining_time = 15 - (current_time - last_request_time).total_seconds()
            await message.answer(
                f"Подождите ещё {int(remaining_time)} секунд перед следующим запросом"
            )
            return
    send_message = await message.answer(
        "Бот генерирует ответ, подождите пару секунд..."
    )
    await state.set_state(Code.wait)
    res = await code_generation(message.text)
    await send_message.answer(res)
    await state.update_data(last_request_time=current_time.isoformat())
    await state.set_state(Code.code)


@user.message(F.text == "Распознавание изображения")
async def fn_vision(message: Message, state: FSMContext):
    await state.set_state(Vision.vision)
    await message.answer(text="Введите ваш запрос...", reply_markup=kb.main2)


@user.message(Vision.vision, F.photo)
async def fn_vision_response(message: Message, state: FSMContext):
    current_time = datetime.now()
    data = await state.get_data()
    last_request_time = data.get("last_request_time")
    if last_request_time:
        last_request_time = datetime.fromisoformat(last_request_time)
        if current_time - last_request_time < timedelta(seconds=15):
            remaining_time = 15 - (current_time - last_request_time).total_seconds()
            await message.answer(
                f"Подождите ещё {int(remaining_time)} секунд перед следующим запросом"
            )
            return
    processing_message = await message.answer(
        "Бот генерирует ответ, подождите пару секунд..."
    )

    async def send_additional_message():
        await asyncio.sleep(5)
        await processing_message.edit_text(
            "Обработка занимает больше времени, пожалуйста, подождите..."
        )

    additional_message_task = asyncio.create_task(send_additional_message())
    try:
        await state.set_state(Vision.wait)
        photo = message.photo[-1]
        file = await message.bot.get_file(photo.file_id)
        photo_path = f"images/{photo.file_id}.jpg"
        await message.bot.download(file.file_id, destination=photo_path)
        caption = message.caption if message.caption else "Опишите это изображение"
        answer = await image_recognition(photo_path, caption)
        if answer is None:
            await message.answer(
                "Извините, произошла ошибка при обработке изображения. Пожалуйста, попробуйте ещё раз."
            )
        else:
            await processing_message.edit_text(answer)
        await state.update_data(last_request_time=current_time.isoformat())
        await state.set_state(Vision.vision)
    except Exception as e:
        print(f"Ошибка: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте ещё раз.")
    finally:
        additional_message_task.cancel()
        os.remove(photo_path)


@user.message(F.text == "Поиск в Интернете")
async def fn_internet(message: Message, state: FSMContext):
    await state.set_state(Internet.internet)
    await message.answer(text="Введите ваш запрос...", reply_markup=kb.main2)


@user.message(Internet.internet)
async def fn_internet_response(message: Message, state: FSMContext):
    current_time = datetime.now()
    data = await state.get_data()
    last_request_time = data.get("last_request_time")
    if last_request_time:
        last_request_time = datetime.fromisoformat(last_request_time)
        if current_time - last_request_time < timedelta(seconds=15):
            remaining_time = 15 - (current_time - last_request_time).total_seconds()
            await message.answer(
                f"Подождите ещё {int(remaining_time)} секунд перед следующим запросом"
            )
            return
    send_message = await message.answer(
        "Бот генерирует ответ, подождите пару секунд..."
    )
    await state.set_state(Internet.wait)
    res = search_with_mistral(message.text)
    await send_message.answer(res)
    await state.update_data(last_request_time=current_time.isoformat())
    await state.set_state(Internet.internet)
