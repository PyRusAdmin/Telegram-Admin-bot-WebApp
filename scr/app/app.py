# -*- coding: utf-8 -*-
import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Query
from fastapi import Form
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger
from starlette.responses import JSONResponse

from scr.bot.system.dispatcher import READ_ONLY, FULL_ACCESS
from scr.utils.get_id import get_participants_count
from scr.utils.models import BadWords, PrivilegedUsers, Groups
from scr.utils.models import Group, db
from scr.utils.models import GroupRestrictions

# Глобальная переменная для бота (устанавливается при запуске)
_bot = None


def set_bot(bot):
    """Установка бота для FastAPI приложения"""
    global _bot
    _bot = bot


def get_bot():
    """Получение бота"""
    if _bot is None:
        raise RuntimeError("Бот не инициализирован")
    return _bot


app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# === Подключаем шаблоны и статику ===
app.mount("/scr/app/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# === Маршруты ===


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Отображение стартовой страницы с приветствием пользователя.

    :param request: Объект запроса.
    :return: HTML-страница с приветствием.
    """
    return templates.TemplateResponse("index.html", {"request": request})


# Новый маршрут для "Ограничения на сообщения"
@app.get("/restrictions_messages")
async def restrictions_messages(request: Request):
    return templates.TemplateResponse(
        "restrictions_messages.html", {"request": request}
    )


# Новый маршрут для "Ограничение по подписке на канал"
@app.get("/channel_subscription_limit")
async def channel_subscription_limit(request: Request):
    return templates.TemplateResponse(
        "channel_subscription_limit.html", {"request": request}
    )


# Новый маршрут для "Фильтр запрещённых слов"
@app.get("/filter_words")
async def filter_words(request: Request):
    return templates.TemplateResponse("filter_words.html", {"request": request})


# Новый маршрут для "Выдать пользователю особые права в группе"
@app.get("/grant_user_special_rights_group")
async def grant_user_special_rights_group(request: Request):
    """
    Отображение страницы с формой для ввода данных о пользователе и группе.

    :param request: Объект запроса.
    :return: HTML-страница с формой для ввода данных о пользователе и группе.
    """
    return templates.TemplateResponse(
        "grant_user_special_rights_group.html", {"request": request}
    )


# Маршрут для "Формирование групп"
@app.get("/formation-groups")
async def formation_groups(request: Request):
    """
    Отображение страницы с формой для ввода username группы.

    :param request: Объект запроса.
    :return: HTML-страница с формой для ввода username группы.
    """
    return templates.TemplateResponse("formation_groups.html", {
        "request": request,
    })


"""Помощь пользователю"""


@app.get("/help")
async def help(request: Request):
    return templates.TemplateResponse("help.html", {"request": request})


"""Формирование групп и каналов для отслеживания сообщений пользователей в группах и каналах"""


@app.get("/add_groups_for_tracking")
async def add_groups_for_tracking(request: Request):
    return templates.TemplateResponse(
        "add_groups_for_tracking.html", {"request": request}
    )


@app.post("/save-username")
async def save_username(username_chat_channel: str = Form(...)):
    try:
        db.create_tables([Groups], safe=True)
        with db.atomic():
            # Удаляем дубликаты (если есть)
            Groups.delete().where(
                Groups.username_chat_channel == username_chat_channel
            ).execute()
            # Добавляем новое значение
            Groups.create(username_chat_channel=username_chat_channel)
        return JSONResponse(content={"success": True})
    except Exception as e:
        print("Ошибка при сохранении:", e)
        return JSONResponse(
            content={"success": False, "error": str(e)}, status_code=500
        )


"""Удаление группы по username группы"""


@app.get("/groups_del")
async def get_groups_dell(chat_title: str):
    group = Group.get(Group.chat_title == chat_title)
    return {"chat_title": group.chat_title, "id_chat": group.chat_id}


@app.post("/delete_group")
async def delete_group(chat_id: int = Form(...), user_id: int = Form(...)):  # <- Добавить user_id
    """Удаление группы по ID группы, принадлежащей пользователю."""
    try:
        # Удаляем группу по chat_id И user_id (для безопасности)
        query = Group.delete().where((Group.chat_id == chat_id) & (Group.user_id == user_id))
        logger.debug(f"Выполняется запрос: {query}")
        deleted_count = query.execute()  # Выполняем запрос
        if deleted_count:
            return {
                "success": True,
                "message": f"Группа с ID '{chat_id}' успешно удалена",
            }
        else:
            return {"success": False, "error": "Группа не найдена или доступ запрещён"}
    except Exception as e:
        logger.error(f"Ошибка при удалении группы: {e}")
        return {"success": False, "error": "Не удалось удалить группу"}


"""Запись данных в базу данных по username группы"""


@app.post("/save-group")
async def save_group(chat_username: str = Form(...), user_id: int = Form(...)):
    """
    Запись данных в базу данных по username группы.

    :param chat_username: Username группы.
    :param user_id: ID пользователя, который добавляет группу.
    """
    try:
        # Удаляем пробелы по краям
        chat_username = chat_username.strip()

        logger.debug(f"Пользователь с ID: {user_id} добавляет группу с username: {chat_username}")

        chat_id, chat_title, chat_total, chat_link = await get_participants_count(chat_username)
        permission_to_write = "True"
        db.create_tables([Group], safe=True)
        with db.atomic():
            Group.insert(
                chat_id=chat_id,
                chat_title=chat_title,
                chat_total=chat_total,
                chat_link=chat_link,
                permission_to_write=permission_to_write,
                user_id=user_id,
            ).execute()
        return RedirectResponse(url="/formation-groups?success=1", status_code=303)
    except Exception as e:
        logger.exception(e)
        return RedirectResponse(url="/formation-groups?error=1", status_code=303)


# Получение списка групп для отображения на странице. Получение списка групп пользователя телеграмм бота
@app.get("/chat_title")
async def get_groups(user_id: int = Query(...)):
    """
    Получение списка групп, для отображения на странице пользователя количества участников. Отображается название
    группы с базы данных.
    Возвращает список групп, принадлежащих пользователю с заданным user_id.
    """
    try:
        groups = list(
            Group
            .select(Group.chat_title)
            .where(Group.user_id == user_id)
            .dicts()
        )
        return {"chat_title": groups}
    except Exception as e:
        return {"chat_title": [], "error": str(e)}


# Количество участников
@app.get("/restrictions_on_messages")
async def restrictions_on_messages(request: Request):
    return templates.TemplateResponse(
        "restrictions_on_messages.html", {"request": request}
    )


@app.get("/get-participants")
async def get_participants(chat_title: str):
    """
    Получение количества участников в группе.
    """
    group = Group.get(Group.chat_title == chat_title)
    # Здесь можно вызвать Telegram API для актуального числа участников
    return {"success": True, "participants_count": group.chat_total}


@app.get("/update-participants")
async def update_participants(chat_title: str):
    """
    Обновление количества участников в группе.
    """
    from aiogram.exceptions import TelegramBadRequest

    try:
        group = Group.get(Group.chat_title == chat_title)

        chat_id, title, total, link = await get_participants_count(group.chat_link)
        Group.update(chat_total=total).where(
            Group.chat_title == chat_title).execute()

        return {"success": True, "participants_count": total}

    except TypeError as e:
        logger.error(e)

    except TelegramBadRequest as e:
        error_msg = str(e)
        if "chat not found" in error_msg.lower():
            logger.warning(f"Чат не найден: {group.chat_title} ({group.chat_link})")
            return {
                "success": False,
                "error": "Бот не состоит в этой группе или не является администратором. Добавьте бота в группу как администратора."
            }
        elif "bot is not an administrator" in error_msg.lower():
            logger.warning(f"Бот не администратор: {group.chat_title} ({group.chat_link})")
            return {
                "success": False,
                "error": "Бот не является администратором в этой группе. Назначьте бота администратором."
            }
        else:
            logger.error(f"Ошибка Telegram API: {e}")
            return {"success": False, "error": f"Ошибка Telegram: {error_msg}"}

    except Exception as e:
        logger.exception(e)
        return {"success": False, "error": str(e)}


# Получение списка групп для отображения на странице
@app.get("/chat_title_groups_select")
async def get_groups():
    """
    Получение списка групп, для отображения на странице пользователя количества участников. Отображается название
    группы с базы данных.
    """
    chat_title = list(Group.select().dicts())
    return {"chat_title": chat_title}


@app.get("/update-restrict-messages")
async def update_restrict_messages(chat_title: str, restricted: bool = True):
    """
    Обновление статуса блокировки сообщений в группе.  Если в группе "False", то блокировка сообщений включена. Если
    "True", то блокировка сообщений выключена.
    """
    try:
        group = Group.get(Group.chat_title == chat_title)
        permission_to_write = "False"
        # Обновляем запись в базе
        Group.update(permission_to_write=permission_to_write).where(
            Group.chat_title == chat_title
        ).execute()
        return {"success": True, "permission_to_write": permission_to_write}
    except Exception as e:
        logger.exception(e)


# 🔒 Установить только чтение
@app.get("/readonly")
async def chat_readonly(chat_id: int):
    """
    Переводит чат в режим «только чтение». Передаваемый chat_id, должен быть в формате -1001234567890, и являться числовым значением.

    :param chat_id: ID чата, в формате -1001234567890
    :return: Словарь с ключами "success" и "message" или "error"
    """
    try:
        chat_id = str(f"-100{chat_id}")
        await get_bot().set_chat_permissions(chat_id=int(chat_id), permissions=READ_ONLY)
        return {"success": True, "message": "Чат переведён в режим «только чтение»"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/writeable")
async def chat_writeable(chat_id: int):
    """
    Переводит чат в режим «все могут писать». Передаваемый chat_id, должен быть в формате -1001234567890, и являться
    числовым значением.

    :param chat_id: ID чата, в формате -1001234567890
    """
    try:
        chat_id = str(f"-100{chat_id}")
        await get_bot().set_chat_permissions(chat_id=chat_id, permissions=FULL_ACCESS)
        return {"success": True, "message": "Чат переведён в режим «все могут писать»"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/set-bad-words")
async def write_bad_words(bad_word: str):
    """
    Записываем плохое слово в базу данных
    """
    try:
        # Получаем информацию о целевой группе (ту, которую хотим ограничить)
        bad_words = BadWords(
            bad_word=bad_word.strip().lower(),  # Получаем слово от пользователя
        )
        bad_words.save()
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/give-privileges")
async def chat_give_privilege(request: Request, chat_title: str = Form(None), user_id: str = Form(None)):
    """
    Запись в базу данных пользователей, которым разрешено писать в чате без ограничений

    :param chat_title: название чата
    :param user_id: id пользователя
    """
    try:
        # Логируем полученные данные
        form_data = await request.form()
        logger.info(f"Получены данные формы: {dict(form_data)}")
        logger.info(f"chat_title: {chat_title}, user_id: {user_id}")

        if not chat_title or not user_id:
            logger.error(f"Отсутствуют обязательные поля: chat_title={chat_title}, user_id={user_id}")
            return {"success": False, "error": "Отсутствуют обязательные поля"}

        logger.info(
            f"Выдача привилегий для пользователя {user_id} в чате '{chat_title}'"
        )
        group = Group.get(Group.chat_title == chat_title)
        logger.info(f"Найдена группа: chat_id={group.chat_id}, chat_title={group.chat_title}")
        group_id = group.chat_id

        existing = (
            PrivilegedUsers.select()
            .where(
                (PrivilegedUsers.chat_id == group_id)
                & (PrivilegedUsers.user_id == int(user_id))
            )
            .first()
        )

        if not existing:
            privileges = PrivilegedUsers(
                chat_id=group_id, user_id=int(user_id), chat_title=chat_title
            )
            privileges.save()
            logger.info(f"Привилегии выданы: user_id={user_id}, chat_id={group_id}")
        else:
            logger.info(f"Привилегии уже существуют: user_id={user_id}, chat_id={group_id}")

        return {
            "success": True,
            "message": f"Пользователь {user_id} теперь имеет привилегии в чате '{chat_title}'",
        }

    except Exception as e:
        logger.exception(f"Ошибка при выдаче привилегий: {e}")
        return {"success": False, "error": str(e)}


@app.get("/get-chat-id")
async def get_chat_id(title: str):
    """
    Получение названия группы
    """
    group = Group.get(Group.chat_title == title)
    return {"success": True, "chat_id": group.chat_id}


@app.get("/require-subscription")
async def chat_subscribe(chat_title: str, required_chat_title: str):
    """
    Устанавливает ограничение на подписку для группы chat_title.
    Пользователи смогут писать только если подписаны на канал/группу required_chat_title.
    """
    try:
        # Получаем информацию о целевой группе (ту, которую хотим ограничить)
        group = Group.get(Group.chat_title == chat_title)
        group_id = group.chat_id
        logger.info(f"Первая группа {group_id}")

        # Получаем информацию о канале/группе, на который нужно подписаться
        required_group = Group.get(Group.chat_title == required_chat_title)
        channel_id = required_group.chat_id  # id канала или группы
        channel_username = required_group.chat_link  # username канала или группы
        logger.info(f"Вторая группа {channel_id}. Username {channel_username}")

        # Обновляем запись в базе
        restriction, created = GroupRestrictions.get_or_create(
            group_id=group_id,
            defaults={
                "required_channel_id": channel_id,
                "required_channel_username": channel_username,
            },
        )
        if not created:
            # Если запись уже существует — обновляем её
            GroupRestrictions.update(
                required_channel_id=channel_id,
                required_channel_username=channel_username,
            ).where(GroupRestrictions.group_id == group_id).execute()

        return {
            "success": True,
            "message": f"Теперь для группы '{chat_title}' требуется подписка на '{required_chat_title}'",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    # Инициализируем бота для работы API
    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties
    from aiogram.client.session.aiohttp import AiohttpSession
    from dotenv import load_dotenv

    load_dotenv()
    bot_token = os.getenv('BOT_TOKEN_2')
    USER = os.getenv('USER')
    PASSWORD = os.getenv('PASSWORD')
    IP = os.getenv('IP')
    PORT = os.getenv('PORT')

    # Настройка прокси через переменные окружения
    from scr.proxy.proxy import setup_proxy

    setup_proxy(USER, PASSWORD, IP, PORT)

    # Создаём сессию (прокси через переменные окружения)
    session = AiohttpSession()
    bot = Bot(token=bot_token, default=DefaultBotProperties(), session=session)

    set_bot(bot)

    uvicorn.run("app:app", host="127.0.0.1", port=8080, reload=True)
