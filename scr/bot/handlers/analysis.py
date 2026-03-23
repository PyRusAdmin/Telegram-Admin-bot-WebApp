# -*- coding: utf-8 -*-
import re

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message
from groq import Groq
from loguru import logger

from scr.YandexWordstatPy.yandex_wordstat_py import yandex_wordstat_py
from scr.bot.states.states import AnalysisState
from scr.config import GROQ_KEY, OAUTH, PASSWORD_PROXY, IP_PROXY, PORT_PROXY, USER_PROXY
from scr.proxy.proxy import setup_proxy

router = Router(name=__name__)


async def get_chat_completion(work: str) -> str:
    """Возвращает ключевые слова из текста поста через ИИ"""
    try:
        setup_proxy(USER_PROXY, PASSWORD_PROXY, IP_PROXY, PORT_PROXY)

        client = Groq(api_key=GROQ_KEY)
        chat_completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "system",
                    "content": "Проанализируй текст и найди ключевые словосочетания. "
                               "Выведи ТОЛЬКО сам список — без нумерации, без тире, без маркеров, без лишнего текста. "
                               "Каждое словосочетание на отдельной строке. Не более 5 словосочетаний.",
                },
                {
                    "role": "user", "content": work
                },
            ],
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        logger.exception(e)
        return "⚠️ Ошибка при обращении к ИИ"


async def get_data_sort(work: str) -> str:
    """Делает общий акализ текста с помощью ИИ"""
    try:
        setup_proxy(USER, PASSWORD_PROXY, IP_PROXY, PORT_PROXY)

        client = Groq(api_key=GROQ_KEY)
        chat_completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": (
                    "Ты — эксперт по анализу поисковых запросов. "
                    "Твоя задача: взять статистику запросов из Яндекс Wordstat и ключевые фразы, "
                    "а затем сделать структурированный анализ. "
                    "Ответ всегда пиши в формате HTML для Telegram.\n\n"
                    "Структура ответа:\n"
                    "1. <b>Топ ключевых фраз</b> (самые важные, объясни почему).\n"
                    "2. <b>Региональный спрос</b> (где чаще ищут, где реже).\n"
                    "3. <b>Вывод</b> — общий анализ + рекомендации."
                )},
                {"role": "user", "content": work},
            ],
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        logger.exception(e)
        return "⚠️ Ошибка при обращении к ИИ"


def ai_text_to_list(text: str) -> list[str]:
    result = []
    for line in text.splitlines():
        # убираем ведущие маркеры: "- ", "• ", "* ", "1. ", "1) "
        line = re.sub(r"^[\s\-•*]+", "", line)
        line = re.sub(r"^\d+[\.\)]\s*", "", line)
        line = line.strip()
        if line:
            result.append(line)
    return result


@router.callback_query(lambda c: c.data == "analysis")
async def analysis_callback(callback: CallbackQuery, state: FSMContext):
    """Отвечает на нажатие кнопки 'Анализ'"""

    text = (
        "🤖 <b>Анализ поста в Telegram</b>\n\n"
        "⚠️ <b>Важно:</b> Бот должен быть <b>администратором</b> в канале/группе, "
        "чтобы прочитать пост. Если бот не администратор — анализ не сработает.\n\n"
        "Вот что сделает бот после того, как вы отправите ссылку на пост:\n\n"
        "1️⃣ Извлечёт текст из поста.\n"
        "2️⃣ AI ✨ определит ключевые фразы.\n"
        "3️⃣ Для каждой фразы будет сделан запрос в "
        '<a href="https://wordstat.yandex.ru">Яндекс Wordstat</a>.\n'
        "4️⃣ 📊 Бот покажет статистику запросов по регионам и частотности.\n\n"
        "👉 Отправьте ссылку на пост, который хотите проанализировать:"
    )

    msg = await callback.message.answer(
        text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
    await state.update_data(prompt_msg_id=msg.message_id)
    await state.set_state(AnalysisState.link_post)
    await callback.answer()


@router.message(AnalysisState.link_post)
async def get_link_post_user(message: Message, state: FSMContext):
    """Получает ссылку от пользователя и анализирует пост через бота"""
    try:
        data = await state.get_data()
        prompt_msg_id = data.get("prompt_msg_id")

        if prompt_msg_id:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=prompt_msg_id)
            except Exception as e:
                logger.warning(f"Не удалось удалить сообщение: {e}")

        try:
            await message.delete()
        except Exception as e:
            logger.warning(f"Не удалось удалить сообщение пользователя: {e}")

        link = message.text.strip()
        logger.info(f"Получена ссылка: {link}")
        await state.update_data(link_post=link)

        match_public = re.match(r"https://t\.me/([^/]+)/(\d+)", link)
        match_private = re.match(r"https://t\.me/c/(\d+)/(\d+)", link)
        logger.info(f"match_public: {match_public}, match_private: {match_private}")

        channel, message_id = None, None
        if match_public:
            channel = "@" + match_public.group(1)  # ← добавить @
            message_id = int(match_public.group(2))
        elif match_private:
            channel_id = int(match_private.group(1))
            message_id = int(match_private.group(2))
            channel = int(f"-100{channel_id}")
        else:
            await message.answer("⚠️ Неверная ссылка. Пришлите ссылку на пост вида https://t.me/username/123")
            await state.clear()
            return

        await message.answer("🔄 Получаю пост из канала...")

        try:
            # Проверяем доступ к каналу
            chat = await message.bot.get_chat(chat_id=channel)
            logger.info(f"Получен чат: {chat.title}, type: {chat.type}")

            # Копируем сообщение для получения текста
            # forward_message возвращает полный Message с .text и .caption
            forward_msg = await message.bot.forward_message(
                chat_id=message.chat.id,
                from_chat_id=channel,
                message_id=message_id
            )
            post_text = forward_msg.text or forward_msg.caption or ""

            # Удаляем пересланное сообщение
            try:
                await message.bot.delete_message(
                    chat_id=message.chat.id,
                    message_id=forward_msg.message_id
                )
            except Exception as e:
                logger.warning(f"Не удалось удалить пересланное сообщение: {e}")

        except TelegramBadRequest as e:
            error_msg = str(e).lower()
            logger.warning(f"TelegramBadRequest при получении поста: {e}")

            if "chat_forward_privacy" in error_msg or "forward_privacy" in error_msg:
                await message.answer(
                    "❌ <b>На канале включена защита контента</b> (запрет пересылки).\n\n"
                    "Отключите её: <i>Настройки канала → Тип канала → Защита контента</i>",
                    parse_mode=ParseMode.HTML
                )
            elif "chat not found" in error_msg or "channel_private" in error_msg:
                await message.answer(
                    "❌ <b>Канал не найден или бот не имеет доступа.</b>\n\n"
                    "Для приватного канала добавьте бота как администратора.",
                    parse_mode=ParseMode.HTML
                )
            elif "message not found" in error_msg or "have no access" in error_msg:
                await message.answer("⚠️ Пост не найден или бот не имеет доступа к нему.")
            else:
                await message.answer(f"❌ Ошибка при получении поста: {e}")

            await state.clear()
            return

        if not post_text.strip():
            await message.answer("⚠️ Пост без текста (возможно только медиа).")
            await state.clear()
            return

        await message.answer("🔄 Обрабатываю текст поста через ИИ...")
        ai_answer = await get_chat_completion(work=post_text)
        await message.answer(f"🤖 Ключевые слова:\n{ai_answer}")
        keywords = ai_text_to_list(ai_answer)
        logger.debug(keywords)

        all_results = []
        for keyword in keywords:
            await message.answer(f"🔎 Анализирую запрос в Wordstat: «{keyword}»...")
            data = yandex_wordstat_py(keyword, OAUTH)
            all_results.append(data)
            await message.answer(f"📊 Данные по «{keyword}»:\n{data}")

        combined_text = "\n\n".join(all_results)
        ai_answer = await get_data_sort(work=combined_text)

        # Очищаем ответ от неподдерживаемых HTML-тегов Telegram
        ai_answer = (
            ai_answer.replace("<h2>", "<b>")
            .replace("</h2>", "</b>")
            .replace("<h1>", "<b>")
            .replace("</h1>", "</b>")
            .replace("<h3>", "<b>")
            .replace("</h3>", "</b>")
            .replace("<p>", "")
            .replace("</p>", "\n")
            .replace("<ul>", "")
            .replace("</ul>", "")
            .replace("<li>", "• ")
            .replace("</li>", "\n")
            .replace("<br>", "\n")
            .replace("<br/>", "\n")
            .replace("<br />", "\n")
        )

        await message.answer(f"🧠 <b>Общий анализ:</b>\n{ai_answer}", parse_mode=ParseMode.HTML)

    except TelegramBadRequest as e:
        error_msg = str(e).lower()
        if "parse entities" in error_msg or "can't parse" in error_msg:
            # Отправляем без HTML, если не удалось распарсить
            await message.answer(f"🧠 Общий анализ:\n{ai_answer}")
        else:
            logger.error(f"Ошибка Telegram: {e}")
            await message.answer("⚠️ Ошибка при отправке ответа.")
    except Exception as e:
        logger.exception(e)
        await message.answer("⚠️ Произошла ошибка при анализе поста.")
    finally:
        await state.clear()
