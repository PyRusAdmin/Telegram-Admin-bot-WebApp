# -*- coding: utf-8 -*-
import requests
from loguru import logger


def get_wordstat_by_regions(keyword: str, OAuth: str, region_type: str = "cities") -> dict | None:
    """
    Получает статистику запросов по регионам из API Яндекс.Вордстат.

    Функция отправляет POST-запрос к API `https://api.wordstat.yandex.net/v1/regions`
    и возвращает данные о частоте запросов для указанного ключевого слова,
    сгруппированные по регионам (страны, регионы, города и т.д.).

    Args:
        keyword (str): Ключевая фраза, по которой нужно получить статистику.
        OAuth (str): OAuth-токен для авторизации в API Яндекса.
        region_type (str, optional): Тип регионов для анализа.
            Возможные значения:
                - "all"      — все регионы;
                - "countries" — только страны;
                - "regions"  — области/регионы;
                - "cities"   — города (по умолчанию).

    Returns:
        dict | None:
            - В случае успеха: JSON-ответ от API в виде словаря Python.
            - В случае ошибки: None (и сообщение об ошибке выводится в лог).

    Raises:
        requests.exceptions.RequestException: Если произошла ошибка соединения или таймаут.

    Пример:
        >>> OAuth = "y0_example_token"
        >>> result = get_wordstat_by_regions("купить ноутбук", OAuth, region_type="regions")
        >>> if result:
        ...     print(result["regions"][0])
        {'regionId': 213, 'name': 'Москва', 'count': 12345, 'share': 0.15, 'affinityIndex': 1.3}
    """

    payload = {
        "phrase": keyword,
        "regionType": region_type,  # all, cities, regions, countries
    }
    HEADERS = {
        "Authorization": f"Bearer {OAuth}",
        "Content-Type": "application/json",
    }
    URL_REGIONS = "https://api.wordstat.yandex.net/v1/regions"  # Для статистики по регионам

    try:
        response = requests.post(URL_REGIONS, json=payload, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"❌ {response.status_code}: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Ошибка запроса: {e}")
        return None
