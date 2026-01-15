# -*- coding: utf-8 -*-
from datetime import datetime

from aiogram import types
from aiogram.filters import Command

from scr.bot.system.dispatcher import bot, router


@router.message(Command("count"))
async def getCountMembers(message: types.Message):
    chat_id = -1001488076358

    # Получаем инфо о чате
    chat = await bot.get_chat(chat_id)

    # Дата (в формате ДД.ММ.ГГГГ)
    now = datetime.now().strftime("%d.%m.%Y")

    # Количество участников
    count = await bot.get_chat_member_count(chat_id)
    await message.answer(
        f"📌 Название: {chat.title}\n"
        f"👥 Количество участников: {count}\n"
        f"🗓 Дата: {now}"
    )


def register_getCountMembers_handlers():
    router.message.register(getCountMembers, Command("count"))
