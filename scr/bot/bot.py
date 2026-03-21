# -*- coding: utf-8 -*-
import asyncio

from aiogram.exceptions import TelegramNetworkError
from loguru import logger  # https://github.com/Delgan/loguru

from scr.bot.handlers.message_moderation_handler import router as moderation_router
from scr.bot.handlers.message_moderation import router as message_moderation
from scr.bot.handlers.admin import router as admin
from scr.bot.handlers.analysis import router as analysis
from scr.bot.handlers.analysis_number_participants import router as analysis_number_participants
from scr.bot.handlers.choose_winner import router as choose_winner
from scr.bot.handlers.member import router as member
from scr.bot.system.dispatcher import dp, bot


async def main():
    """
    Главная асинхронная функция для запуска бота.
    Здесь инициализируются обработчики команд и запускается polling.
    """

    try:
        logger.info("Бот запущен")
        dp.include_router(admin)  # Подключение роутера для обработки админ-команд
        dp.include_router(analysis)  # Подключение роутера для аналитики
        dp.include_router(analysis_number_participants)  # Подключение роутера для анализа количества участников
        dp.include_router(choose_winner)  # Подключение роутера для выбора победителя
        dp.include_router(member)  # Подключение роутера для обработки действий участников
        dp.include_router(message_moderation)  # Регистрация обработчика для получения ID сообщений и записи в базу данных
        dp.include_router(moderation_router)  # Регистрация обработчиков для модерации (например, проверка подписки)

        await dp.start_polling(bot)  # Запуск бота с использованием Dispatcher

    except TelegramNetworkError:
        logger.error(" Нет возможности запустить бота (прокси, токен, интернет)")

    except Exception as error:
        logger.exception(error)  # Логирование исключений, если что-то пошло не так


if __name__ == "__main__":  # Точка входа в программу
    asyncio.run(main())  # Запуск асинхронной главной функции
