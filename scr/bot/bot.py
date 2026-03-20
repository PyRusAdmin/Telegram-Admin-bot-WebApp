# -*- coding: utf-8 -*-
import asyncio

import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramNetworkError
from loguru import logger  # https://github.com/Delgan/loguru

from scr.bot.handlers.admin import register_send_id_handler
from scr.bot.handlers.analysis import register_analysis_handler
from scr.bot.handlers.analysis_number_participants import register_getCountMembers_handlers
from scr.bot.handlers.choose_winner import register_choose_winer_handler
from scr.bot.handlers.member import register_member_handlers
from scr.bot.handlers.message_moderation import register_get_id_ban
from scr.bot.handlers.message_moderation_handler import register_subscription_handlers
from scr.bot.system.dispatcher import (
    dp, router,
    bot_token_2,
    USER, PASSWORD, IP, PORT
)
from scr.proxy.proxy import setup_proxy


async def main():
    """
    Главная асинхронная функция для запуска бота.
    Здесь инициализируются обработчики команд и запускается polling.
    """
    try:
        # Настройка прокси для ОС
        setup_proxy(USER, PASSWORD, IP, PORT)

        # Создание сессии с прокси для aiogram
        proxy_url = f"http://{USER}:{PASSWORD}@{IP}:{PORT}" if all([USER, PASSWORD, IP, PORT]) else None
        connector = aiohttp.TCPConnector(ssl=False)
        session = aiohttp.ClientSession(connector=connector, proxy=proxy_url) if proxy_url else aiohttp.ClientSession(connector=connector)

        bot = Bot(
            token=bot_token_2,
            default=DefaultBotProperties(),
            session=AiohttpSession(session=session)
        )

        logger.info("Бот запущен")
        register_subscription_handlers()  # Регистрация обработчиков для подписки
        register_send_id_handler()  # Регистрация обработчика для отправки ID
        register_member_handlers()  # Регистрация обработчиков для членов
        register_choose_winer_handler()  # Регистрация обработчика для выбора победителя
        register_analysis_handler()  # Регистрация обработчика для анализа
        register_getCountMembers_handlers()  # Регистрация обработчика для получения количества участников

        register_get_id_ban()  # Регистрация обработчика для получения ID и записи в базу данных

        await dp.start_polling(bot)  # Запуск бота с использованием Dispatcher

    except TelegramNetworkError:
        logger.error(" Нет возможности запустить бота (прокси, токен, интернет)")

    except Exception as error:
        logger.exception(error)  # Логирование исключений, если что-то пошло не так

    finally:
        # Закрытие сессии при остановке
        await session.close()
        await bot.session.close()


if __name__ == "__main__":  # Точка входа в программу
    asyncio.run(main())  # Запуск асинхронной главной функции
