import sys
import os
import asyncio
from unittest.mock import AsyncMock, MagicMock

# Добавляем корень проекта в PYTHONPATH
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import pytest
from aiogram.types import Message, Chat, User
from scr.bot.handlers.admin import send_id


def run_async(coro):
    """Запускает асинхронную функцию в синхронном тесте."""
    return asyncio.new_event_loop().run_until_complete(coro)


@pytest.fixture
def mock_message():
    """Создаёт мок объекта Message для тестирования."""
    message = MagicMock(spec=Message)
    message.from_user = User(id=123456, first_name="Test", is_bot=False)
    message.chat = Chat(id=789012, type="group")
    message.message_id = 999
    message.bot = AsyncMock()
    message.delete = AsyncMock()
    return message


@pytest.fixture
def mock_chat_member_admin():
    """Создаёт мок объекта ChatMember для администратора."""
    chat_member = MagicMock()
    chat_member.status = "administrator"
    return chat_member


@pytest.fixture
def mock_chat_member_user():
    """Создаёт мок объекта ChatMember для обычного пользователя."""
    chat_member = MagicMock()
    chat_member.status = "member"
    return chat_member


@pytest.fixture
def mock_replied_user():
    """Создаёт мок объекта пользователя из ответного сообщения."""
    user = MagicMock()
    user.first_name = "Reply"
    user.last_name = "User"
    user.id = 555666
    return user


def test_send_id_admin_with_reply(mock_message, mock_chat_member_admin, mock_replied_user):
    """
    Тест: администратор отвечает на сообщение — должен получить ID пользователя.
    """
    # Настраиваем моки
    mock_message.bot.get_chat_member = AsyncMock(return_value=mock_chat_member_admin)
    mock_message.reply_to_message = MagicMock()
    mock_message.reply_to_message.from_user = mock_replied_user
    mock_message.bot.get_chat = AsyncMock(return_value=mock_replied_user)
    mock_message.bot.send_message = AsyncMock()
    mock_message.bot.delete_message = AsyncMock()

    # Вызываем функцию
    run_async(send_id(mock_message))

    # Проверяем, что администратору отправлено сообщение с ID
    mock_message.bot.send_message.assert_called_once_with(
        chat_id=mock_message.from_user.id,
        text=f"Пользователь: {mock_replied_user.first_name} {mock_replied_user.last_name}\nID: {mock_replied_user.id}",
    )
    # Проверяем, что исходное сообщение удалено
    mock_message.bot.delete_message.assert_called_once()


def test_send_id_not_admin(mock_message, mock_chat_member_user):
    """
    Тест: обычный пользователь (не админ) — должен получить отказ.
    """
    mock_message.bot.get_chat_member = AsyncMock(return_value=mock_chat_member_user)
    mock_message.bot.send_message = AsyncMock()

    run_async(send_id(mock_message))

    # Проверяем, что отправлено сообщение об отказе
    mock_message.bot.send_message.assert_called_once_with(
        chat_id=mock_message.chat.id,
        text="Команда доступна только для администраторов.",
    )
    # Проверяем, что сообщение удалено
    mock_message.delete.assert_called_once()


def test_send_id_no_reply(mock_message, mock_chat_member_admin):
    """
    Тест: администратор не ответил на сообщение — должна быть ошибка.
    """
    mock_message.bot.get_chat_member = AsyncMock(return_value=mock_chat_member_admin)
    mock_message.reply_to_message = None  # Нет ответного сообщения
    mock_message.bot.send_message = AsyncMock()

    run_async(send_id(mock_message))

    # Проверяем, что отправлено сообщение об ошибке
    mock_message.bot.send_message.assert_called_once_with(
        chat_id=mock_message.chat.id,
        text="Ответьте на сообщение пользователя, чтобы узнать его ID",
    )
