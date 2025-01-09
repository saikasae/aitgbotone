import os
from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware, Bot
from aiogram.types import Message, CallbackQuery
from app.keyboards import get_subs_keyboard

class CheckSubscribeMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        message: Message | CallbackQuery,
        data: Dict[str, Any],
    ):
        user = message.from_user
        group = os.getenv('GROUP')
        try:
            user_subscription_status = await message.bot.get_chat_member(
                chat_id=group,
                user_id=user.id
            )

            status = str(user_subscription_status).split()[0][8:-1]
            if status == 'left':
                await message.answer('👋 Для того, чтобы пользоваться ботом, вам необходимо подписаться на наш канал.\n'
                         'После подписки, нажмите на соответствующую кнопку.', reply_markup=get_subs_keyboard()
                )
                return
            return await handler(message, data)
        except Exception as e:
            print(f'Произошла ошибка: {e}')
            await message.answer("Произошла ошибка! Попробуйте снова.")
            return
