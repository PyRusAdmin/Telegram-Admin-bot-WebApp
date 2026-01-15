# -*- coding: utf-8 -*-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo


def create_admin_panel_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для главного меню"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛠 Панель администратора",
                    web_app=WebAppInfo(url="https://mybotadmin.ru.tuna.am"),
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎯 Выбрать победителя конкурса",
                    callback_data="choose_winner"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Ключевые слова",
                    callback_data="analysis"
                )
            ],
        ]
    )
    return keyboard
