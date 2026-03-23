# -*- coding: utf-8 -*-

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ChatPermissions

from scr.config import USER, PASSWORD, IP, PORT, bot_token_2

READ_ONLY = ChatPermissions(can_send_messages=False)
FULL_ACCESS = ChatPermissions(can_send_messages=True)

storage = MemoryStorage()
dp = Dispatcher(storage=storage)


def create_bot():
    """Создание бота с SOCKS5 прокси"""
    # Используем SOCKS5 прокси через URL
    session = AiohttpSession(proxy=f"socks5://{USER}:{PASSWORD}@{IP}:{PORT}")

    return Bot(
        token=bot_token_2,
        default=DefaultBotProperties(),
        session=session
    )


bot = None
