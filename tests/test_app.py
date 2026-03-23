import sys
import os

# Добавляем корень проекта в PYTHONPATH для импорта модулей
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from fastapi.testclient import TestClient
from scr.app.app import app

client = TestClient(app)


def test_index_page():
    """
    Тест проверяет, что главная страница возвращает статус 200 и содержит ожидаемый контент.
    """
    response = client.get("/")

    assert response.status_code == 200
    assert "<html" in response.text.lower() or "<!doctype html" in response.text.lower(), "Страница не содержит HTML"
    assert "добро пожаловать" in response.text.lower() or "привет" in response.text.lower(), "Приветствие не найдено на странице"


def test_help_page():
    """
    Тест проверяет, что страница помощи возвращает статус 200.
    """
    response = client.get("/help")
    assert response.status_code == 200


def test_formation_groups_page():
    """
    Тест проверяет, что страница формирования групп возвращает статус 200.
    """
    response = client.get("/formation-groups")
    assert response.status_code == 200


def test_restrictions_on_messages_page():
    """
    Тест проверяет, что страница ограничений на сообщения возвращает статус 200.
    """
    response = client.get("/restrictions_on_messages")
    assert response.status_code == 200


def test_favicon():
    """
    Тест проверяет, что favicon возвращает статус 204 (No Content).
    """
    response = client.get("/favicon.ico")
    assert response.status_code == 204


def test_chat_title_with_user_id():
    """
    Тест проверяет, что /chat_title с user_id возвращает статус 200.
    """
    response = client.get("/chat_title", params={"user_id": 123456})
    assert response.status_code == 200
    data = response.json()
    assert "chat_title" in data
