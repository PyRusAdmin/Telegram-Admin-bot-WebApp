# -*- coding: utf-8 -*-
from datetime import datetime

from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from loguru import logger

from scr.bot.system.dispatcher import bot, router
from scr.utils.models import get_id_grup_for_administration, get_chat_link_by_chat_id


@router.message(Command("count"))
async def getCountMembers(message: types.Message):
    try:
        user_id = message.from_user.id  # Получаем ID пользователя

        list_id_grup = get_id_grup_for_administration(user_id=user_id)
        logger.info(list_id_grup)

        for chat_id in list_id_grup:

            # Преобразуем "голый" ID в ID супергруппы
            if not str(chat_id).startswith('-100'):
                actual_chat_id = int(f"-100{chat_id}")
            else:
                actual_chat_id = chat_id

            try:
                chat = await bot.get_chat(chat_id=actual_chat_id)
                count = await bot.get_chat_member_count(chat_id=actual_chat_id)
                now = datetime.now().strftime("%d.%m.%Y")
                await message.answer(
                    f"📌 Название: {chat.title}\n"
                    f"👥 Количество участников: {count}\n"
                )
            except TelegramBadRequest:
                now = datetime.now().strftime("%d.%m.%Y")
                # display_name = f"@{username}" if username else title

                display_name = get_chat_link_by_chat_id(chat_id, user_id)

                await message.answer(
                    f"⚠️ Бот не состоит в {display_name}\n"
                    f"ID: {chat_id}\n"
                    "Добавьте бота в чат как администратора."
                )

    except Exception as e:
        logger.exception(e)


def register_getCountMembers_handlers():
    router.message.register(getCountMembers, Command("count"))
