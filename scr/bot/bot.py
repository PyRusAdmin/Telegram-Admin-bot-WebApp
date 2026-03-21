# -*- coding: utf-8 -*-
import asyncio

from aiogram.exceptions import TelegramNetworkError
from loguru import logger  # https://github.com/Delgan/loguru

# from scr.bot.handlers.admin import register_send_id_handler
# from scr.bot.handlers.analysis import register_analysis_handler
# from scr.bot.handlers.analysis_number_participants import register_getCountMembers_handlers
# from scr.bot.handlers.choose_winner import register_choose_winer_handler
# from scr.bot.handlers.member import register_member_handlers
# from scr.bot.handlers.message_moderation import register_get_id_ban
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
        # Создание сессии с прокси для aiogram 3.x

        logger.info("Бот запущен")
        # register_subscription_handlers()
        # register_send_id_handler()  # Регистрация обработчика для отправки ID
        # register_member_handlers()  # Регистрация обработчиков для членов
        # register_choose_winer_handler()  # Регистрация обработчика для выбора победителя
        # register_analysis_handler()  # Регистрация обработчика для анализа
        # register_getCountMembers_handlers()  # Регистрация обработчика для получения количества участников

        # register_get_id_ban()
        dp.include_router(admin)  # Регистрация обработчика для отправки ID
        dp.include_router(analysis)
        dp.include_router(analysis_number_participants)
        dp.include_router(choose_winner)
        dp.include_router(member)
        dp.include_router(message_moderation)  # Регистрация обработчика для получения ID и записи в базу данных
        dp.include_router(moderation_router)  # Регистрация обработчиков для подписки

        await dp.start_polling(bot)  # Запуск бота с использованием Dispatcher

    except TelegramNetworkError:
        logger.error(" Нет возможности запустить бота (прокси, токен, интернет)")

    except Exception as error:
        logger.exception(error)  # Логирование исключений, если что-то пошло не так


if __name__ == "__main__":  # Точка входа в программу
    asyncio.run(main())  # Запуск асинхронной главной функции
