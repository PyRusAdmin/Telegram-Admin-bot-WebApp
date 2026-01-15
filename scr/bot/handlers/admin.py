# -*- coding: utf-8 -*-
from aiogram.filters import Command
from aiogram.types import Message
from loguru import logger

from scr.bot.system.dispatcher import bot
from scr.bot.system.dispatcher import router


@router.message(Command("id"))
async def send_id(message: Message):
    """Обработчик команды /id"""
    logger.info(
        f"Пользователь {message.from_user.id} вызвал команду '/id' в чате {message.chat.id}"
    )
    # Проверяем, является ли пользователь админом в текущем чате
    chat_member = await bot.get_chat_member(
        chat_id=message.chat.id, user_id=message.from_user.id
    )
    if chat_member.status not in ["administrator", "creator"]:
        # Если пользователь не является админом, отправляем ему сообщение с предупреждением
        await bot.send_message(
            message.chat.id, "Команда доступна только для администраторов."
        )
        await message.delete()  # Удаляем сообщение с командой /id
        return
    try:
        # получаем ID пользователя, который написал сообщение
        # получаем информацию о пользователе по его ID
        user = await bot.get_chat(message.reply_to_message.from_user.id)
        # отправляем ID, имя и фамилию пользователя в личку
        await bot.send_message(
            chat_id=message.from_user.id,
            text=f"Пользователь: {user.first_name} {user.last_name}\nID: {user.id}",
        )
        # удаляем сообщение с командой /id
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except AttributeError:
        # если произошла ошибка AttributeError, то сообщаем об этом пользователю
        await bot.send_message(
            chat_id=message.chat.id,
            text="Ответьте на сообщение пользователя, чтобы узнать его ID",
        )


def register_send_id_handler() -> None:
    router.message.register(send_id, Command("id"))
