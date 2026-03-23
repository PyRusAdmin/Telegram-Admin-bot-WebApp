# -*- coding: utf-8 -*-
import os

from dotenv import load_dotenv

# Загружаем .env из корня проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))

GROQ_KEY = os.getenv('GROQ_KEY')
USER = os.getenv('USER_PROXY')
PASSWORD = os.getenv('PASSWORD')
PORT = os.getenv('PORT')
IP = os.getenv('IP')
OAuth = os.getenv('OAuth')

bot_token = os.getenv('BOT_TOKEN_2')

bot_token_2 = os.getenv('BOT_TOKEN_2')
time_del = os.getenv('TIME_DEL')
