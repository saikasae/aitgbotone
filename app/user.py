import base64
import os
from datetime import datetime, timedelta
from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message
import app.keyboards as kb
from app.database.requests import set_user
from app.generators import (
    code_generation,
    image_generation,
    image_recognition,
    search_with_mistral,
    text_generation,
)
from app.middleware.subscribe_middleware import CheckSubscribeMiddleware
from app.states import Code, Image, Internet, Text, Vision
from app.utils.trim_history import trim_history

user = Router()
user.message.middleware(CheckSubscribeMiddleware())
user.callback_query.middleware(CheckSubscribeMiddleware())

history = {}


@user.callback_query()
async def check_query(message: CallbackQuery, state: FSMContext):
    if str(message.data) == "subscribe":
        await set_user(message.from_user.id)
        await message.bot.send_message(
            text="Добро пожаловать! Выберите один из пунктов меню",
            reply_markup=kb.get_main_keyboard(),
            chat_id=message.from_user.id,
        )
        await state.clear()


@user.message(CommandStart())
async def cmnd_start(message: Message, state: FSMContext):
    await set_user(message.from_user.id)
    await message.answer(text="Добро пожаловать!", reply_markup=kb.get_main_keyboard())
    await state.clear()


@user.message(F.text == "Назад в меню")
async def cmnd_close(message: Message, state: FSMContext):
    await set_user(message.from_user.id)
    await message.answer(
        text="Вы вернулись в меню!",
        reply_markup=kb.get_main_keyboard(),
    )
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
    await message.answer(
        text="Введите ваш запрос...",
        reply_markup=kb.get_main2_keyboard(),
    )


@user.message(Text.text)
async def fn_text_response(message: Message, state: FSMContext):
    current_time = datetime.now()
    data = await state.get_data()
    last_request_time = data.get("last_request_time")
    if last_request_time:
        last_request_time = datetime.fromisoformat(last_request_time)
        if current_time - last_request_time < timedelta(seconds=10):
            remaining_time = 10 - (current_time - last_request_time).total_seconds()
            await message.answer(
                f"Подождите ещё {int(remaining_time)} секунд перед следующим запросом",
            )
            return

    send_message = await message.answer(
        "Бот думает над ответом, подождите пару секунд...",
    )

    await state.set_state(Text.wait)

    if message.from_user.id not in history:
        history[message.from_user.id] = []

    history[message.from_user.id].append({"role": "user", "content": message.text})
    history[message.from_user.id] = await trim_history(
        history[message.from_user.id],
        max_length=4096,
        max_messages=5,
    )

    answer_data = await text_generation(history[message.from_user.id])

    if not answer_data or not isinstance(answer_data, dict):
        raise ValueError("Неверный формат ответа от модели")

    text_response = answer_data.get("text")
    image_response = answer_data.get("image")

    history[message.from_user.id].append({"role": "assistant", "content": text_response})
    history[message.from_user.id] = await trim_history(
        history[message.from_user.id],
        max_length=4096,
        max_messages=5,
    )

    if image_response:
        image_bytes = base64.b64decode(image_response)
        await message.answer_photo(photo=BufferedInputFile(image_bytes, filename="latex.png"))
    else:
        await send_message.answer(text_response)

    await state.update_data(last_request_time=current_time.isoformat())
    await state.set_state(Text.text)


@user.message(F.text == "Генерация изображения")
async def fn_image(message: Message, state: FSMContext):
    await state.set_state(Image.image)
    await message.answer(
        text="Введите ваш запрос...",
        reply_markup=kb.get_main2_keyboard(),
    )


@user.message(Image.image)
async def fn_image_response(message: Message, state: FSMContext):
    current_time = datetime.now()
    data = await state.get_data()
    last_request_time = data.get("last_request_time")
    if last_request_time:
        last_request_time = datetime.fromisoformat(last_request_time)
        if current_time - last_request_time < timedelta(seconds=10):
            remaining_time = 10 - (current_time - last_request_time).total_seconds()
            await message.answer(
                f"Подождите ещё {int(remaining_time)} секунд перед следующим запросом",
            )
            return

    send_message = await message.answer(
        "Бот генерирует ответ, подождите пару секунд...",
    )
    await state.set_state(Image.wait)
    answer = await image_generation(message.text)
    image_bytes = base64.b64decode(answer)
    await send_message.answer_photo(
        photo=BufferedInputFile(file=image_bytes, filename="generated_image.jpg"),
    )
    generated_images_dir = "generated_images"
    if os.path.exists(generated_images_dir):
        for distribution in os.listdir(generated_images_dir):
            file_path = os.path.join(generated_images_dir, distribution)
            if os.path.isfile(file_path):
                os.remove(file_path)
                os.rmdir(generated_images_dir)

    await state.update_data(last_request_time=current_time.isoformat())
    await state.set_state(Image.image)


@user.message(F.text == "Генерация кода")
async def fn_code(message: Message, state: FSMContext):
    await state.set_state(Code.code)
    await message.answer(
        text="Введите ваш запрос...",
        reply_markup=kb.get_main2_keyboard(),
    )


@user.message(Code.code)
async def fn_code_response(message: Message, state: FSMContext):
    current_time = datetime.now()
    data = await state.get_data()
    last_request_time = data.get("last_request_time")
    if last_request_time:
        last_request_time = datetime.fromisoformat(last_request_time)
        if current_time - last_request_time < timedelta(seconds=10):
            remaining_time = 10 - (current_time - last_request_time).total_seconds()
            await message.answer(
                f"Подождите ещё {int(remaining_time)} секунд перед следующим запросом",
            )
            return

    send_message = await message.answer(
        "Бот генерирует ответ, подождите пару секунд...",
    )
    await state.set_state(Code.wait)
    if message.from_user.id not in history:
        history[message.from_user.id] = []

    history[message.from_user.id].append({"role": "user", "content": message.text})
    history[message.from_user.id] = await trim_history(
        history[message.from_user.id],
        max_length=4096,
        max_messages=5,
    )
    answer = await code_generation(history[message.from_user.id])
    if not answer:
        raise ValueError("Пустой ответ от модели")

    history[message.from_user.id].append({"role": "assistant", "content": answer})
    history[message.from_user.id] = await trim_history(
        history[message.from_user.id],
        max_length=4096,
        max_messages=5,
    )
    await send_message.answer(answer)
    await state.update_data(last_request_time=current_time.isoformat())
    await state.set_state(Code.code)


@user.message(F.text == "Распознавание изображения")
async def fn_vision(message: Message, state: FSMContext):
    await state.set_state(Vision.vision)
    await message.answer(
        text="Введите ваш запрос...",
        reply_markup=kb.get_main2_keyboard(),
    )


@user.message(Vision.vision, F.photo)
async def fn_vision_response(message: Message, state: FSMContext):
    current_time = datetime.now()
    data = await state.get_data()
    last_request_time = data.get("last_request_time")
    if last_request_time:
        last_request_time = datetime.fromisoformat(last_request_time)
        if current_time - last_request_time < timedelta(seconds=10):
            remaining_time = 10 - (current_time - last_request_time).total_seconds()
            await message.answer(
                f"Подождите ещё {int(remaining_time)} секунд перед следующим запросом",
            )
            return

    processing_message = await message.answer(
        "Бот генерирует ответ, подождите пару секунд...",
    )
    try:
        await state.set_state(Vision.wait)
        photo = message.photo[-1]
        get_file = await message.bot.get_file(photo.file_id)
        photo_path = f"images/{photo.file_id}.jpg"
        await message.bot.download(get_file.file_id, destination=photo_path, timeout=90)
        caption = (
            message.caption
            if message.caption
            else "Опиши это изображение как можно подробнее"
        )
        answer = await image_recognition(photo_path, caption)
        if answer is None:
            await message.answer(
                "Извините, произошла ошибка при обработке изображения. Пожалуйста, попробуйте ещё раз",
            )
        else:
            await processing_message.edit_text(answer)

        await state.update_data(last_request_time=current_time.isoformat())
        await state.set_state(Vision.vision)
    except Exception as e:
        print(f"Ошибка: {type(e).__name__}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте ещё раз")
    finally:
        os.remove(photo_path)


@user.message(F.text == "Поиск в Интернете (beta-версия)")
async def fn_internet(message: Message, state: FSMContext):
    await state.set_state(Internet.internet)
    await message.answer(
        text="Введите ваш запрос...",
        reply_markup=kb.get_main2_keyboard(),
    )


@user.message(Internet.internet)
async def fn_internet_response(message: Message, state: FSMContext):
    current_time = datetime.now()
    data = await state.get_data()
    last_request_time = data.get("last_request_time")
    if last_request_time:
        last_request_time = datetime.fromisoformat(last_request_time)
        if current_time - last_request_time < timedelta(seconds=10):
            remaining_time = 10 - (current_time - last_request_time).total_seconds()
            await message.answer(
                f"Подождите ещё {int(remaining_time)} секунд перед следующим запросом",
            )
            return

    send_message = await message.answer(
        "Бот генерирует ответ, подождите пару секунд...",
    )
    await state.set_state(Internet.wait)
    res = await search_with_mistral(message.text)
    await send_message.answer(res)
    await state.update_data(last_request_time=current_time.isoformat())
    await state.set_state(Internet.internet)
