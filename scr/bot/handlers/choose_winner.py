import random
import re

from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (
    CallbackQuery
)
from aiogram.types import Message
from loguru import logger
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest

from scr.bot.system.dispatcher import router, api_id, api_hash

SESSION_NAME = "session_name_1"


class ChooseWinnerState(StatesGroup):
    waiting_for_link = State()


@router.callback_query(lambda c: c.data == "choose_winner")
async def choose_winner_callback(callback: CallbackQuery):
    await callback.message.answer("Пришлите ссылку на пост в Telegram для выбора победителя:")
    await callback.answer()


async def parse_telegram_link(link: str):
    pattern = r"(?:https?://)?t\.me/([\w\d_+-]+)/(\d+)"
    match = re.match(pattern, link)
    if match:
        return match.group(1), int(match.group(2))
    return None, None


async def get_random_commenter(channel_username, post_id):
    async with TelegramClient(f"scr/setting/{SESSION_NAME}", api_id, api_hash) as client:
        await client.connect()
        try:
            await client(JoinChannelRequest(channel_username))
        except Exception as e:
            logger.error(f"Ошибка подписки: {e}")

        commenters = []
        async for msg in client.iter_messages(channel_username, reply_to=post_id, reverse=True):
            sender_id = msg.from_id.user_id if msg.from_id else None
            username = msg.sender.username if msg.sender else None
            if sender_id:
                commenters.append((sender_id, username))

        await client.disconnect()

    return random.choice(commenters) if commenters else None


# Этот хендлер с фильтром, чтобы не пересекаться с unified_message_handler
@router.message(lambda m: re.match(r"(?:https?://)?t\.me/[\w\d_+-]+/\d+", m.text or ""))
async def handle_post_link(message: Message):
    channel_username, post_id = await parse_telegram_link(message.text.strip())
    if not channel_username or not post_id:
        await message.reply("⚠️ Некорректная ссылка. Формат: https://t.me/channel/123")
        return

    random_commenter = await get_random_commenter(channel_username, post_id)
    if random_commenter:
        user_id, username = random_commenter
        await message.reply(f"🎉 Победитель: @{username} (ID: {user_id})")
    else:
        await message.reply("❌ Не удалось найти комментаторов.")


def register_choose_winer_handler() -> None:
    router.callback_query.register(choose_winner_callback)  # правильная регистрация
    router.message.register(handle_post_link)
