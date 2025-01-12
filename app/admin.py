from aiogram import Router
from aiogram.filters import Command, Filter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.database.requests import get_users
from app.states import Mailing

admin = Router()


class Admin(Filter):
    async def __call__(self, message: Message):
        return message.from_user.id in [667393044]


@admin.message(Admin(), Command("mailing"))
async def mailing(message: Message, state: FSMContext):
    await state.set_state(Mailing.message)
    await message.answer("Введите сообщение...")


@admin.message(Mailing.message)
async def mailing_message(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Рассылка началась")
    users = await get_users()
    for user in users:
        try:
            await message.send_copy(chat_id=user.tg_id)
        except Exception as e:
            print(e)

    await message.answer("Рассылка завершена")
