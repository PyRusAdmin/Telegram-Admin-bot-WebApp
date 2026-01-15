# -*- coding: utf-8 -*-
import datetime

from aiogram import F
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from aiogram.types import ChatMemberUpdated
from aiogram.types import Message
from loguru import logger

# Импорты из системы
from scr.bot.system.dispatcher import router  # Экземпляр диспетчера (бота и роутера)
from scr.utils.models import GroupMembers


@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def handle_new_member(event: ChatMemberUpdated):
    """
    Обработчик события добавления нового участника в группу.
    Записывает информацию с новом участнике в базу данных.

    IS_NOT_MEMBER >> IS_MEMBER - Участник только что присоединился к группе.
    (https://docs.aiogram.dev/en/latest/dispatcher/filters/chat_member_updated.html#usage)
    """
    try:
        # Записываем данные о новом участнике в базу данных
        group = GroupMembers(
            chat_id=event.chat.id,  # Получаем ID чата
            chat_title=event.chat.title,  # Получаем название чата
            user_id=event.from_user.id,  # Получаем ID пользователя, который зашел в группу
            # Получаем username пользователя, который вступил в группу
            username=event.from_user.username or "",  # Если username не указан, то записываем пустую строку
            # Получаем имя пользователя который вступил в группу
            first_name=event.from_user.first_name,
            # Получаем фамилию пользователя который вступил в группу
            last_name=event.from_user.last_name,
            date_now=datetime.datetime.now(),  # Текущее время
        )
        group.save()
    except Exception as error:
        logger.exception(f"Ошибка обработки добавления нового участника: {error}")


@router.chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
async def handle_member_left(event: ChatMemberUpdated):
    """
    Обработчик события выхода участника из группы.
    Записывает информацию о вышедшем участнике в базу данных.

    IS_MEMBER >> IS_NOT_MEMBER - Участник только что покинул группу.
    (https://docs.aiogram.dev/en/latest/dispatcher/filters/chat_member_updated.html#usage)
    """
    try:
        # Записываем данные о новом участнике в базу данных
        group = GroupMembers(
            chat_id=event.chat.id,  # Получаем ID чата
            chat_title=event.chat.title,  # Получаем название чата
            user_id=event.from_user.id,  # Получаем ID пользователя, который зашел в группу
            # Получаем username пользователя, который вступил в группу
            username=event.from_user.username or "",  # Если username не указан, то записываем пустую строку
            # Получаем имя пользователя который вступил в группу
            first_name=event.from_user.first_name,
            # Получаем фамилию пользователя который вступил в группу
            last_name=event.from_user.last_name,
            date_now=datetime.datetime.now(),  # Текущее время
        )
        group.save()
    except Exception as error:
        logger.exception(f"Ошибка обработки выхода участника: {error}")


@router.message(F.new_chat_members)
async def delete_system_message_new_member(message: Message):
    """
    Обработчик удаления системного сообщения о вступлении нового участника в группу.

    Тип сообщения: new_chat_members (https://docs.aiogram.dev/en/v3.1.1/api/enums/content_type.html)
    """
    await message.delete()  # Удаляем системное сообщение
    logger.info("Удаляем системное сообщение")


@router.message(F.left_chat_member)
async def delete_system_message_member_left(message: Message):
    """
    Обработчик удаления системного сообщения о выходе участника из группы.

    Тип сообщения: left_chat_member (https://docs.aiogram.dev/en/v3.1.1/api/enums/content_type.html)
    """
    await message.delete()  # Удаляем системное сообщение
    logger.info("Удаляем системное сообщение")


def register_member_handlers() -> None:
    router.message.register(delete_system_message_new_member)
    router.message.register(delete_system_message_member_left)
