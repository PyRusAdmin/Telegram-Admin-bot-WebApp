# -*- coding: utf-8 -*-
import os

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ChatPermissions
from dotenv import load_dotenv

# Загружаем .env из корня проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))

GROQ_KEY = os.getenv('GROQ_KEY')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
PORT = os.getenv('PORT')
IP = os.getenv('IP')
OAuth = os.getenv('OAuth')

# api_id = int(os.getenv('id'))
# api_hash = os.getenv('hash')

bot_token_2 = os.getenv('BOT_TOKEN_2')
time_del = os.getenv('TIME_DEL')

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
