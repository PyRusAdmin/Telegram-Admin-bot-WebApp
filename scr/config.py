# -*- coding: utf-8 -*-
import os

from dotenv import load_dotenv

# Загружаем .env из корня проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))

GROQ_KEY = os.getenv('GROQ_KEY')
USER_PROXY = os.getenv('USER_PROXY')
PASSWORD_PROXY = os.getenv('PASSWORD')
PORT_PROXY = os.getenv('PORT')
IP_PROXY = os.getenv('IP')
OAuth = os.getenv('OAuth')
BOT_TOKEN = os.getenv('BOT_TOKEN_2')
TIME_DEL = os.getenv('TIME_DEL')
