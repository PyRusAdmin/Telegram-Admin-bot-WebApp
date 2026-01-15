# -*- coding: utf-8 -*-
import os

from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ChatPermissions
from dotenv import load_dotenv

SESSION_NAME = "session_name_1"

load_dotenv(dotenv_path='.env')

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

# config = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)
# Считываем токен бота с файла config.ini
# config.read("scr/setting/config.ini")
# bot_token_2 = config.get('BOT_TOKEN', 'BOT_TOKEN_2')
# time_del = config.get('TIME_DEL', 'TIME_DEL')

# === Права для чата ===
READ_ONLY = ChatPermissions(can_send_messages=False)  # Запрещено писать в чат
FULL_ACCESS = ChatPermissions(can_send_messages=True)  # Разрешено писать в чат

# Инициализация бота и диспетчера
bot = Bot(token=bot_token_2)

storage = MemoryStorage()  # Хранилище
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)
