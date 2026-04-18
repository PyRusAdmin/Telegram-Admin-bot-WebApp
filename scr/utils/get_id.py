# -*- coding: utf-8 -*-
from aiogram.exceptions import TelegramBadRequest
from loguru import logger

from scr.bot.system.dispatcher import bot


async def get_participants_count(chat_link):
    """
    Получение количества участников чата через бота (aiogram)

    :param chat_link: Ссылка на чат
    """
    try:
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


async def get_chat_info_by_id(chat_id):
    """
    Получение информации о чате по ID через бота (aiogram).
    Бот должен быть администратором в группе для получения username.

    :param chat_id: ID чата (например: -1001234567890, -1234567890 или 1234567890)
    :return: tuple (chat_id, chat_title, total_users, chat_link)
    """
    try:
        # Удаляем пробелы по краям
        chat_id = chat_id.strip()
        
        # Обрабатываем разные форматы ID
        if chat_id.startswith('-100'):
            # Уже в правильном формате для супергрупп/каналов
            chat_id_int = int(chat_id)
        elif chat_id.startswith('-'):
            # Обычная группа с минусом
            chat_id_int = int(chat_id)
        else:
            # Число без префикса - определяем тип
            chat_id_num = int(chat_id)
            if chat_id_num > 0:
                # Положительное число - это ID супергруппы/канала
                # Нужно добавить префикс -100
                chat_id_int = int(f"-100{chat_id_num}")
            else:
                # Отрицательное число - уже в формате Telegram
                chat_id_int = chat_id_num
        
        logger.debug(f"Получение информации о чате с ID: {chat_id_int}")

        # Получение информации о чате
        chat = await bot.get_chat(chat_id_int)
        
        # Формируем ссылку на чат
        if chat.username:
            chat_link = f"@{chat.username}"
        else:
            # Приватная группа без username
            chat_link = f"https://t.me/c/{str(chat_id_int).replace('-100', '').replace('-', '')}"
        
        # Получение количества участников
        total_users = await bot.get_chat_member_count(chat_id_int)

        logger.info(f"Получена информация о чате: ID={chat.id}, Title={chat.title}, "
                   f"Username={chat.username}, Members={total_users}")

        return chat.id, chat.title, total_users, chat_link
        
    except TelegramBadRequest as e:
        error_msg = str(e)
        if "chat not found" in error_msg.lower():
            logger.error(f"Чат с ID {chat_id} не найден. Возможно, бот не является участником группы.")
            raise Exception(f"Чат не найден. Убедитесь, что бот добавлен в группу как администратор.")
        elif "bot is not an administrator" in error_msg.lower():
            logger.error(f"Бот не является администратором в чате {chat_id}")
            raise Exception(f"Бот должен быть администратором в группе для получения информации.")
        else:
            logger.error(f"Ошибка Telegram при получении чата {chat_id}: {e}")
            raise
    except Exception as e:
        logger.exception(f"Ошибка при получении информации о чате {chat_id}: {e}")
        raise
