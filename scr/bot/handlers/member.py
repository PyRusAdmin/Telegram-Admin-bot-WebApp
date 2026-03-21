# -*- coding: utf-8 -*-
import datetime

from aiogram import F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from aiogram.types import ChatMemberUpdated
from aiogram.types import Message
from loguru import logger
from aiogram import Router
from scr.utils.models import GroupMembers

router = Router(name=__name__)


@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def handle_new_member(event: ChatMemberUpdated):
    """
    Обработчик события добавления нового участника в группу.
    Записывает информацию с новом участнике в базу данных.

    IS_NOT_MEMBER >> IS_MEMBER - Участник только что присоединился к группе.
    """
    try:
        group = GroupMembers(
            chat_id=event.chat.id,
            chat_title=event.chat.title,
            user_id=event.from_user.id,
            username=event.from_user.username or "",
            first_name=event.from_user.first_name,
            last_name=event.from_user.last_name,
            date_now=datetime.datetime.now(),
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
    """
    try:
        group = GroupMembers(
            chat_id=event.chat.id,
            chat_title=event.chat.title,
            user_id=event.from_user.id,
            username=event.from_user.username or "",
            first_name=event.from_user.first_name,
            last_name=event.from_user.last_name,
            date_now=datetime.datetime.now(),
        )
        group.save()
    except Exception as error:
        logger.exception(f"Ошибка обработки выхода участника: {error}")


@router.message(F.new_chat_members)
async def delete_system_message_new_member(message: Message):
    """
    Обработчик удаления системного сообщения о вступлении нового участника в группу.
    """
    try:
        await message.delete()
        logger.info("Удаляем системное сообщение")
    except TelegramBadRequest as e:
        logger.warning(e)
    except Exception as e:
        logger.exception(e)


@router.message(F.left_chat_member)
async def delete_system_message_member_left(message: Message):
    """
    Обработчик удаления системного сообщения о выходе участника из группы.
    """
    try:
        await message.delete()
        logger.info("Удаляем системное сообщение")
    except TelegramBadRequest as e:
        logger.warning(e)
    except Exception as e:
        logger.exception(e)
