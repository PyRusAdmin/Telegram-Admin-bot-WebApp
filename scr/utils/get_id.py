# -*- coding: utf-8 -*-
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import PeerChat

from scr.bot.system.dispatcher import api_id, api_hash


async def get_participants_count(chat_link):
    async with TelegramClient('scr/setting/session_name_1', api_id, api_hash) as client:
        # Получение сущности чата (канал, группа, пользователь)
        try:
            entity = await client.get_entity(chat_link)

            # Для каналов
            if hasattr(entity, 'broadcast') and entity.broadcast:
                full_info = await client(GetFullChannelRequest(channel=entity))
                total_users = full_info.full_chat.participants_count
            # Для групп (чатов)
            elif hasattr(entity, 'megagroup') and entity.megagroup:
                full_info = await client(GetFullChannelRequest(channel=entity))
                total_users = full_info.full_chat.participants_count
            # Для старых чатов (PeerChat)
            elif isinstance(entity, PeerChat):
                chat = await client.get_entity(entity)
                total_users = chat.participants_count
            else:
                raise ValueError("Неизвестный тип чата")

            return entity.id, entity.title, total_users, chat_link

        except Exception as e:
            raise ValueError(
                f"Ошибка при получении данных для {chat_link}: {e}")
