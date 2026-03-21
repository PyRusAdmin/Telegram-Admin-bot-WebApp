# -*- coding: utf-8 -*-
import os

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ChatPermissions
from dotenv import load_dotenv

SESSION_NAME = "session_name_1"

# Загружаем .env из корня проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))

GROQ_KEY = os.getenv('GROQ_KEY')  # GROQ_KEY
USER = os.getenv('USER')  # логин для прокси
PASSWORD = os.getenv('PASSWORD')  # пароль для прокси
PORT = os.getenv('PORT')  # порт для прокси
IP = os.getenv('IP')  # IP для прокси
OAuth = os.getenv('OAuth')  # OAuth для прокси

# === Телеграм (api_id и api_hash для управления аккаунтом) ===
api_id = os.getenv('id')  # api_id
api_hash = os.getenv('hash')  # api_hash

bot_token_2 = os.getenv('BOT_TOKEN_2')  # Токен бота
time_del = os.getenv('TIME_DEL')  # Время удаления сообщений

# === Права для чата ===
READ_ONLY = ChatPermissions(can_send_messages=False)  # Запрещено писать в чат
FULL_ACCESS = ChatPermissions(can_send_messages=True)  # Разрешено писать в чат

# Инициализация диспетчера и роутера
storage = MemoryStorage()  # Хранилище
dp = Dispatcher(storage=storage)

# router = Router()
# dp.include_router(router)

# Создание сессии с прокси для подключения к Telegram
session = AiohttpSession(
    proxy=f"http://{USER}:{PASSWORD}@{IP}:{PORT}"
)  # Используется HTTP-прокси с аутентификацией для обхода блокировок

# Инициализация бота с токеном, настройками по умолчанию и прокси-сессией
bot = Bot(
    token=bot_token_2,  # Токен Telegram-бота из переменных окружения
    default=DefaultBotProperties(),  # Применение стандартных свойств бота (например, parse_mode)
    session=session  # Подключение сессии с прокси для работы бота
)
