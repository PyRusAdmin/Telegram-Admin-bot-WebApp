# -*- coding: utf-8 -*-
import requests
from loguru import logger

from scr.YandexWordstatPy.getting_region import parse_region_tree


def get_regions_tree(OAuth):
    """
    Загружает полный список регионов из API Яндекс.Вордстат и формирует словарь
    сопоставления ID региона с его названием.

    Функция отправляет POST-запрос на метод API /v1/getRegionsTree, получает дерево
    регионов (страны, регионы, города) и преобразует его в плоский словарь вида:
        {region_id (int): region_name (str)}

    Args:
        OAuth (str): OAuth-токен для авторизации в API Яндекс.Вордстат.

    Returns:
        dict: Словарь, где ключ — ID региона (int), а значение — название региона (str).
              Если произошла ошибка запроса или ответ пустой, возвращается пустой словарь {}.

    Пример использования:
        >>> region_map = get_regions_tree(OAuth="ваш_токен")
        >>> print(region_map[213])
        'Москва'

    Логирование:
        - В случае успешной загрузки выводится количество загруженных регионов.
        - В случае ошибки или пустого ответа выводится соответствующее сообщение об ошибке.

    Внутренние функции:
        - parse_region_tree: используется для рекурсивного обхода дерева регионов
          и формирования плоского словаря region_map.
    """
    try:
        URL_REGIONS_TREE = "https://api.wordstat.yandex.net/v1/getRegionsTree"
        HEADERS = {
            "Authorization": f"Bearer {OAuth}",
            "Content-Type": "application/json",
        }
        response = requests.post(URL_REGIONS_TREE, headers=HEADERS)
        response.raise_for_status()

        tree = response.json()

        if not tree:
            logger.error("❌ Ответ от /v1/getRegionsTree пустой")
            return {}

        region_map = {}
        parse_region_tree(tree, region_map)
        logger.success(f"✅ Загружено {len(region_map)} регионов")
        return region_map

    except Exception as e:
        logger.error(f"❌ Ошибка при загрузке дерева регионов: {e}")
        return {}
