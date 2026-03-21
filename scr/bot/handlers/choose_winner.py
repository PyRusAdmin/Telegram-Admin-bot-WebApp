# -*- coding: utf-8 -*-
import random
import re

from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery
from aiogram.types import Message
from loguru import logger
from aiogram import Router
from scr.bot.system.dispatcher import bot
from peewee import Model, SqliteDatabase, IntegerField, CharField, DateTimeField, IntegrityError
from datetime import datetime

db = SqliteDatabase("comments.db")


class BaseModel(Model):
    class Meta:
        database = db


class Comment(BaseModel):
    """Комментарий к посту канала."""
    channel_id = IntegerField()  # ID канала
    post_id = IntegerField()  # ID поста в канале
    user_id = IntegerField()  # ID пользователя
    username = CharField(null=True)  # @username (может отсутствовать)
    first_name = CharField(default="")
    created_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = "comments"
        # один пользователь — одна запись на пост (без дублей)
        indexes = (
            (("channel_id", "post_id", "user_id"), True),
        )


def init_db():
    db.connect(reuse_if_open=True)
    db.create_tables([Comment], safe=True)


router = Router(name=__name__)

init_db()


# ─── Сборщик комментариев ───────────────────────────────────────────────────
# Бот должен быть админом в группе комментариев.
# Каждое новое сообщение-комментарий к посту канала сохраняется в БД.

@router.message(lambda m: (
        m.reply_to_message is not None
        and m.reply_to_message.forward_from_chat is not None
        and m.reply_to_message.forward_from_message_id is not None
        and m.from_user is not None
        and not m.from_user.is_bot
))
async def collect_comment(message: Message):
    # Данные берём из пересланного поста, на который ответил пользователь
    channel_id = message.reply_to_message.forward_from_chat.id
    post_id    = message.reply_to_message.forward_from_message_id

    try:
        Comment.create(
            channel_id = channel_id,
            post_id    = post_id,
            user_id    = message.from_user.id,
            username   = message.from_user.username,
            first_name = message.from_user.first_name or "",
        )
        logger.debug(
            f"Сохранён комментатор {message.from_user.id} "
            f"к посту {channel_id}/{post_id}"
        )
    except IntegrityError:
        pass  # пользователь уже есть в базе по этому посту


# ─── Вспомогательные функции ───────────────────────────────────────────────

async def parse_telegram_link(link: str):
    pattern = r"(?:https?://)?t\.me/([\w\d_+-]+)/(\d+)"
    match = re.match(pattern, link)
    if match:
        return match.group(1), int(match.group(2))
    return None, None


async def get_random_commenter(channel: str, post_id: int):
    """
    Возвращает случайного комментатора из БД для указанного поста.
    """
    # Получаем числовой ID канала через Bot API
    try:
        chat = await bot.get_chat(chat_id=channel if channel.startswith("@") else f"@{channel}")
        channel_id = chat.id
        logger.info(f"Канал: {chat.title}, ID: {channel_id}")
    except TelegramBadRequest as e:
        error_msg = str(e).lower()
        if "chat not found" in error_msg or "private" in error_msg:
            raise ValueError("Бот не является администратором в этом канале")
        elif "have no access" in error_msg:
            raise ValueError("Бот не имеет доступа к каналу")
        raise

    # Запрашиваем уникальных комментаторов поста из БД
    rows = list(
        Comment
        .select()
        .where(
            Comment.channel_id == channel_id,
            Comment.post_id    == post_id,
            )
        .namedtuples()
    )

    logger.info(f"Найдено комментаторов в базе: {len(rows)}")

    if not rows:
        return None

    winner = random.choice(rows)
    display = f"@{winner.username}" if winner.username else f"id{winner.user_id}"
    return winner.user_id, display


# ─── Хэндлеры ──────────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data == "choose_winner")
async def choose_winner_callback(callback: CallbackQuery):
    text = (
        "🎉 <b>Выбор победителя</b>\n\n"
        "⚠️ <b>Важно:</b> Бот должен быть <b>администратором</b> в канале/группе, "
        "чтобы собирать комментарии. Комментарии копятся с момента запуска бота.\n\n"
        "👉 Пришлите ссылку на пост с комментариями:"
    )
    await callback.message.answer(text, parse_mode=ParseMode.HTML)
    await callback.answer()


@router.message(lambda m: re.match(r"(?:https?://)?t\.me/[\w\d_+-]+/\d+", m.text or ""))
async def handle_post_link(message: Message):
    try:
        channel_username, post_id = await parse_telegram_link(message.text.strip())
        if not channel_username or not post_id:
            await message.reply("⚠️ Некорректная ссылка. Формат: https://t.me/channel/123")
            return

        await message.reply("🔄 Ищу победителя в базе...")

        try:
            random_commenter = await get_random_commenter(channel_username, post_id)
        except ValueError as e:
            await message.reply(
                f"❌ <b>Ошибка:</b> {str(e)}\n\n"
                f"Для выбора победителя бот должен быть администратором в канале.",
                parse_mode=ParseMode.HTML,
            )
            return
        except Exception as e:
            await message.reply(f"❌ Ошибка: {e}")
            return

        if random_commenter:
            user_id, username = random_commenter
            await message.reply(
                f"🎉 <b>Победитель:</b> {username} (ID: <code>{user_id}</code>)",
                parse_mode=ParseMode.HTML,
            )
        else:
            await message.reply(
                "❌ Комментаторов не найдено в базе.\n\n"
                "Возможные причины:\n"
                "• Бот был запущен после того, как оставили комментарии\n"
                "• Бот не администратор в группе комментариев\n"
                "• Неверная ссылка на пост"
            )

    except Exception as e:
        logger.exception(e)
        await message.reply("⚠️ Произошла ошибка при выборе победителя.")