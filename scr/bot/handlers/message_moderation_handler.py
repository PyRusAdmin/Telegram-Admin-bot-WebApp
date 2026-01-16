# -*- coding: utf-8 -*-
import asyncio

from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, JOIN_TRANSITION
from aiogram.types import Message, ChatMemberUpdated, ChatPermissions
from loguru import logger
from peewee import DoesNotExist

from scr.bot.keyboard.keyboard import create_admin_panel_keyboard
from scr.bot.messages.translations_loader import translations
from scr.bot.system.dispatcher import bot
from scr.bot.system.dispatcher import router
from scr.bot.system.dispatcher import time_del
from scr.utils.models import BadWords, get_privileged_users, save_bot_user, BannedUser, log_spam
from scr.utils.models import GroupRestrictions


@router.message()
async def unified_message_handler(message: Message) -> None:
    """
    Универсальный хендлер для обработки всех входящих сообщений:
    - проверка подписки на канал;
    - фильтрация пересланных сообщений;
    - фильтрация запрещённых слов;
    - фильтрация ссылок;
    - реакция на команду /start.
    """
    logger.debug("Хендлер сработал")
    chat_id = message.chat.id
    user_id = message.from_user.id
    logger.debug(f"chat_id: {chat_id}, user_id: {user_id}")

    # Проверяем, есть ли пользователь в списке заблокированных
    try:
        BannedUser.get(BannedUser.user_id == user_id)

        # 🔥 ЛОГИРУЕМ как спамера
        log_spam(
            user_id=user_id,
            chat_id=chat_id,
            chat_title=message.chat.title,
            violation_type="banned_user",  # или "blacklisted_user"
            message_text=message.text if message.text else None
        )

        # Пользователь найден — применяем ограничения
        permissions = ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False,
        )
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=user_id,
            permissions=permissions
        )
        # Удаляем сообщение
        await message.delete()
        # Опционально: отправить уведомление (лучше в личку или лог-канал)
        # await bot.send_message(user_id, "Вы ограничены в этой группе за нарушение правил.")
    except DoesNotExist:
        # Пользователь не заблокирован — ничего не делаем
        pass
    except Exception as e:
        # Например, бот не может ограничить админа — пропускаем
        # В продакшене: залогируйте ошибку
        pass

    # Преобразуем в строку и убираем -100
    normalized_chat_id = int(str(chat_id).replace("-100", ""))
    privileged_users = get_privileged_users()
    logger.debug(f"privileged_users: {privileged_users}")

    # Если личка, просто реагируем на /start
    if message.chat.type == "private":
        if message.text == "/start":
            # сохраняем юзера
            await save_bot_user(message)

            logger.info(f"Пользователь {user_id} прислал команду /start")
            await bot.send_message(
                chat_id,
                translations["ru"]["menu"]["user"],
                reply_markup=create_admin_panel_keyboard(),
                parse_mode="HTML",
            )
        return

    # Проверка подписки на канал
    try:
        clean_id = str(message.chat.id)[4:]
        restriction = GroupRestrictions.get_or_none(
            GroupRestrictions.group_id == clean_id
        )
        if restriction:
            required_channel_id = restriction.required_channel_id
            required_channel_username = restriction.required_channel_username
            channel_chat_id = f"-100{required_channel_id}"

            member = await bot.get_chat_member(chat_id=channel_chat_id, user_id=user_id)
            if member.status not in [
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.CREATOR,
            ]:
                await message.delete()
                bot_message = await message.answer(
                    f"{message.from_user.mention_html()}, привет! 👋 Чтобы писать в группе, подпишись на канал {required_channel_username}. Это временная мера — спасибо за понимание! 🌟",
                    parse_mode="HTML",
                )
                await asyncio.create_task(delete_message_after_delay(bot_message, 60))
                return
    except Exception as e:
        logger.exception(f"Ошибка при проверке подписки: {e}")
        await message.delete()
        user_mention = (
            message.from_user.mention_html()
            if message.from_user.username
            else f"User {user_id}"
        )
        restriction = GroupRestrictions.get(GroupRestrictions.group_id == clean_id)
        channel_username = restriction.required_channel_username
        bot_message = await message.answer(
            f"{user_mention}, привет! 👋 Чтобы писать в группе, подпишись на канал {channel_username}. Это временная мера — спасибо за понимание! 🌟",
            parse_mode="HTML",
        )
        await asyncio.create_task(delete_message_after_delay(bot_message, 60))
        return

    # Пропускаем модерацию для привилегированных пользователей
    if (normalized_chat_id, user_id) in privileged_users:
        return

    # Проверка на пересланное сообщение
    if message.forward_from or message.forward_from_chat:
        await message.delete()
        warning = await message.answer(
            translations["ru"]["message_moderation"]["moderation_forward_message"],
            parse_mode="HTML",
        )
        await asyncio.sleep(int(time_del))
        await warning.delete()
        return

    # Проверка текста на запрещенные слова
    if message.text:
        bad_words = list(set(word.bad_word for word in BadWords.select()))
        for word in bad_words:
            if word.lower() in message.text.lower():
                try:
                    await message.delete()
                except TelegramBadRequest:
                    logger.error("Ошибка при удалении сообщения (уже удалено)")
                warning = await message.answer(
                    translations["ru"]["message_moderation"]["moderation_bad_words"],
                    parse_mode="HTML",
                )
                await asyncio.sleep(int(time_del))
                await warning.delete()
                return

    # Проверка на ссылки и упоминания
    if message.text and message.entities:
        for entity in message.entities:
            if entity.type in ["url", "text_link", "mention"]:
                try:
                    await message.delete()
                except TelegramBadRequest:
                    logger.error("Ошибка при удалении сообщения (уже удалено)")
                warning = await message.answer(
                    translations["ru"]["message_moderation"]["moderation_url_message"],
                    parse_mode="HTML",
                )
                await asyncio.sleep(int(time_del))
                await warning.delete()
                return


@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def on_chat_member_update(update: ChatMemberUpdated):
    """Снимает ограничения с пользователя, если он подписался на канал"""
    if update.new_chat_member.status not in [
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.ADMINISTRATOR,
    ]:
        return
    try:
        # Чистим ID канала от префикса -100 перед поиском в базе
        clean_channel_id = str(update.chat.id)[4:]  # -> "2022404388"
        # Находим все группы, где требуется подписка на этот канал
        query = GroupRestrictions.select(GroupRestrictions.group_id).where(
            GroupRestrictions.required_channel_id == clean_channel_id
        )
        # Получаем список ID групп
        groups = list(query.tuples())
        for group_tuple in groups:
            # Получаем group_id из кортежа (предполагается, что select вернул один столбец)
            group_id = group_tuple[0]
            try:
                member = await bot.get_chat_member(
                    chat_id=group_id, user_id=update.user.id
                )
                if member.status == ChatMemberStatus.RESTRICTED:
                    await bot.restrict_chat_member(
                        chat_id=group_id,
                        user_id=update.user.id,
                        permissions=ChatPermissions(can_send_messages=True),
                    )
                    logger.info(
                        f"Пользователь {update.user.id} разблокирован в группе {group_id}"
                    )
            except Exception as e:
                logger.error(
                    f"Ошибка при снятии ограничений для группы {group_id}: {e}"
                )
                continue
    except Exception as e:
        logger.error(f"Ошибка при обработке события JOIN_TRANSITION: {e}")


async def delete_message_after_delay(message: Message, delay: int):
    """Удаляет сообщение через заданное количество секунд"""
    await asyncio.sleep(delay)
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception as e:
        logger.error(f"Ошибка при удалении сообщения: {e}")


def register_subscription_handlers() -> None:
    router.chat_member.register(on_chat_member_update)
    router.message.register(unified_message_handler)
    router.chat_member.register(on_chat_member_update)
