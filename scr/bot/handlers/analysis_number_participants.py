# -*- coding: utf-8 -*-
from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from loguru import logger

from scr.bot.system.dispatcher import bot, router
from scr.utils.models import get_id_grup_for_administration, get_chat_link_by_chat_id


@router.message(Command("count"))
async def getCountMembers(message: types.Message):
    try:
        user_id = message.from_user.id
        list_id_grup = get_id_grup_for_administration(user_id=user_id)
        logger.info(list_id_grup)

        response_lines = []

        for chat_id in list_id_grup:
            # Преобразуем "голый" ID в ID супергруппы
            if not str(chat_id).startswith('-100'):
                actual_chat_id = int(f"-100{chat_id}")
            else:
                actual_chat_id = chat_id

            try:
                chat = await bot.get_chat(chat_id=actual_chat_id)
                count = await bot.get_chat_member_count(chat_id=actual_chat_id)
                response_lines.append(
                    f"📌 Название: {chat.title}\n"
                    f"👥 Количество участников: {count}"
                )
            except TelegramBadRequest:
                display_name = get_chat_link_by_chat_id(chat_id, user_id)
                response_lines.append(
                    f"⚠️ Бот не состоит в {display_name}\n"
                    f"ID: {chat_id}\n"
                    "Добавьте бота в чат как администратора."
                )
            except Exception as e:
                logger.exception(e)
                response_lines.append(f"❌ Ошибка при обработке чата с ID {chat_id}")

        # Отправляем всё одним сообщением
        if response_lines:
            full_response = "\n\n".join(response_lines)
            # Telegram имеет лимит на длину сообщения (~4096 символов)
            # Если текст слишком длинный — можно разбить на части
            if len(full_response) <= 4096:
                await message.answer(full_response)
            else:
                # Разбиваем на части по 4096 символов с учётом границ строк
                while full_response:
                    part = full_response[:4096]
                    if len(part) == 4096:
                        # Пытаемся не обрезать посреди строки
                        last_newline = part.rfind("\n\n")
                        if last_newline != -1:
                            part = part[:last_newline]
                            full_response = full_response[last_newline + 2:]
                        else:
                            full_response = full_response[4096:]
                    else:
                        full_response = ""
                    await message.answer(part)
        else:
            await message.answer("Нет доступных чатов для отображения.")

    except Exception as e:
        logger.exception(e)
        await message.answer("Произошла ошибка при получении данных.")


def register_getCountMembers_handlers():
    router.message.register(getCountMembers, Command("count"))