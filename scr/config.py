# -*- coding: utf-8 -*-
import os

from dotenv import load_dotenv

# Загружаем .env из корня проекта
load_dotenv()

GROQ_KEY = os.getenv('GROQ_KEY')
USER_PROXY = os.getenv('USER_PROXY')
PASSWORD_PROXY = os.getenv('PASSWORD_PROXY')
PORT_PROXY = os.getenv('PORT_PROXY')
IP_PROXY = os.getenv('IP_PROXY')
OAUTH = os.getenv('OAUTH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
TIME_DEL = os.getenv('TIME_DEL')
