# -*- coding: utf-8 -*-

from aiogram import types
from aiogram.filters import Command

from scr.bot.system.dispatcher import router
from scr.utils.models import BannedUser


@router.message(Command("id_ban"))
async def get_id_ban(message: types.Message):
    """Принимает команду /id_ban <user_id> и записывает ID в базу данных."""
    args = message.text.split()[1:]

    if not args:
        await message.answer("Пожалуйста, укажите ID пользователя. Пример: /id_ban 123456789")
        return

    user_id_str = args[0]

    if not user_id_str.isdigit():
        await message.answer("ID должен быть числом. Пример: /id_ban 123456789")
        return

    user_id = int(user_id_str)

    try:
        # Проверяем, не существует ли уже такой записи
        if BannedUser.get_or_none(BannedUser.user_id == user_id):
            await message.answer(f"ID {user_id} уже находится в списке заблокированных.")
        else:
            BannedUser.create(user_id=user_id)
            await message.answer(f"ID {user_id} успешно добавлен в список заблокированных.")
    except Exception as e:
        # Лучше логировать ошибку, но для простоты — сообщение
        await message.answer("Произошла ошибка при сохранении в базу данных.")
        # В продакшене: logger.error(e)


def register_get_id_ban() -> None:
    router.message.register(get_id_ban)
