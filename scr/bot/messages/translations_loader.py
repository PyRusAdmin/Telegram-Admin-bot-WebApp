# -*- coding: utf-8 -*-
import yaml


def load_translations():
    """Загрузка текста для бота"""
    with open("scr/bot/messages/translations.yaml", "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


translations = load_translations()
