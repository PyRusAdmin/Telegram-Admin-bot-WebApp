# -*- coding: utf-8 -*-
from aiogram.filters import Command
from aiogram.types import Message
from loguru import logger
from aiogram import Router

router = Router(name=__name__)


@router.message(Command("id"))
async def send_id(message: Message):
    """Обработчик команды /id"""
    try:
        logger.info(
            f"Пользователь {message.from_user.id} вызвал команду '/id' в чате {message.chat.id}"
        )
        # Проверяем, является ли пользователь админом в текущем чате
        chat_member = await message.bot.get_chat_member(
            chat_id=message.chat.id, user_id=message.from_user.id
        )
        if chat_member.status not in ["administrator", "creator"]:
            await message.bot.send_message(
                chat_id=message.chat.id, text="Команда доступна только для администраторов."
            )
            await message.delete()
            return
        try:
            user = await message.bot.get_chat(message.reply_to_message.from_user.id)
            await message.bot.send_message(
                chat_id=message.from_user.id,
                text=f"Пользователь: {user.first_name} {user.last_name}\nID: {user.id}",
            )
            await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        except AttributeError:
            await message.bot.send_message(
                chat_id=message.chat.id,
                text="Ответьте на сообщение пользователя, чтобы узнать его ID",
            )
    except Exception as e:
        logger.exception(e)
