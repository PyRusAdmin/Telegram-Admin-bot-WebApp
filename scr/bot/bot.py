# -*- coding: utf-8 -*-
import asyncio

from loguru import logger  # https://github.com/Delgan/loguru

from scr.bot.handlers.admin import register_send_id_handler
from scr.bot.handlers.analysis import register_analysis_handler
from scr.bot.handlers.analysis_number_participants import register_getCountMembers_handlers
from scr.bot.handlers.choose_winner import register_choose_winer_handler
from scr.bot.handlers.member import register_member_handlers
from scr.bot.handlers.message_moderation_handler import register_subscription_handlers
from scr.bot.system.dispatcher import bot, dp

# Настройка логирования: указываем файл, размер ротации и сжатие
logger.add("scr/setting/log/log.log", rotation="1 MB", compression="zip")


async def main():
    """
    Главная асинхронная функция для запуска бота.
    Здесь инициализируются обработчики команд и запускается polling.
    """
    try:
        logger.info("Бот запущен")
        register_subscription_handlers()  # Регистрация обработчиков для подписки
        register_send_id_handler()  # Регистрация обработчика для отправки ID
        register_member_handlers()  # Регистрация обработчиков для членов

        register_choose_winer_handler()  # Регистрация обработчика для выбора победителя

        register_analysis_handler()  # Регистрация обработчика для анализа

        register_getCountMembers_handlers()

        await dp.start_polling(bot)
    except Exception as error:
        # Логирование исключений, если что-то пошло не так
        logger.exception(error)


# Точка входа в программу
if __name__ == "__main__":
    # Запуск асинхронной главной функции
    asyncio.run(main())
