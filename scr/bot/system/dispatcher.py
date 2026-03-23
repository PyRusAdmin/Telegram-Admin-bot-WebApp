# -*- coding: utf-8 -*-
from aiogram import Bot
from aiogram import Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ChatPermissions

from scr.config import PASSWORD_PROXY, IP_PROXY, PORT_PROXY, BOT_TOKEN, USER_PROXY

READ_ONLY = ChatPermissions(can_send_messages=False)
FULL_ACCESS = ChatPermissions(can_send_messages=True)

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Используем SOCKS5 прокси через URL
session = AiohttpSession(proxy=f"socks5://{USER_PROXY}:{PASSWORD_PROXY}@{IP_PROXY}:{PORT_PROXY}")

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(),
    session=session
)
