# -*- coding: utf-8 -*-
import asyncio

from aiogram.client import bot
from aiogram.exceptions import TelegramNetworkError
from loguru import logger

from scr.bot.handlers.admin import router as admin
from scr.bot.handlers.analysis import router as analysis
from scr.bot.handlers.analysis_number_participants import router as analysis_number_participants
from scr.bot.handlers.choose_winner import router as choose_winner
from scr.bot.handlers.member import router as member
from scr.bot.handlers.message_moderation import router as message_moderation
from scr.bot.handlers.message_moderation_handler import router as moderation_router
from scr.bot.system.dispatcher import dp


async def main():
    """
    Главная асинхронная функция для запуска бота.
    """
    # Устанавливаем бота в модули, которые используют его

    try:
        logger.info("Бот запущен")
        dp.include_router(admin)
        dp.include_router(analysis)
        dp.include_router(analysis_number_participants)
        dp.include_router(choose_winner)
        dp.include_router(member)
        dp.include_router(message_moderation)
        dp.include_router(moderation_router)

        await dp.start_polling(bot)

    except TelegramNetworkError:
        logger.error("Нет возможности запустить бота (прокси, токен, интернет)")

    except Exception as error:
        logger.exception(error)


if __name__ == "__main__":
    asyncio.run(main())
