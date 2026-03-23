# -*- coding: utf-8 -*-
from aiogram.exceptions import TelegramBadRequest
from loguru import logger

# Глобальная переменная для бота (устанавливается извне)
_bot = None


def set_bot(bot):
    """Установка бота"""
    global _bot
    _bot = bot


def get_bot():
    """Получение бота"""
    if _bot is None:
        raise RuntimeError("Бот не инициализирован")
    return _bot


async def get_participants_count(chat_link):
    """
    Получение количества участников чата через бота (aiogram)

    :param chat_link: Ссылка на чат
    """
    try:
        bot = get_bot()
        # Удаляем пробелы по краям
        chat_link = chat_link.strip()

        # Получение информации о чате
        chat = await bot.get_chat(chat_link)

        # Получение количества участников
        total_users = await bot.get_chat_member_count(chat_link)

        return chat.id, chat.title, total_users, chat_link
    except TelegramBadRequest as e:
        logger.warning(e)
    except Exception as e:
        logger.exception(e)
        raise
