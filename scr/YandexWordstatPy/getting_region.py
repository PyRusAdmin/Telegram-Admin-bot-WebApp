# -*- coding: utf-8 -*-


def parse_region_tree(node, region_map):
    """
    Рекурсивно обходит дерево регионов и формирует плоский словарь
    сопоставления ID региона с его названием.

    Дерево регионов обычно приходит из API Яндекс.Вордстат в формате JSON,
    где каждый регион представлен объектом с ключами:
        - "value" — уникальный идентификатор региона;
        - "label" — название региона;
        - "children" — список дочерних регионов (может быть пустым или None).

    Функция обходит все уровни вложенности (страны → регионы → города)
    и добавляет каждый регион в словарь region_map.

    Args:
        node (dict | list): Текущий узел дерева регионов.
            Может быть словарем с ключами "value", "label", "children"
            или списком таких словарей.
        region_map (dict): Словарь, куда будут записаны регионы.
            Ключ — int (ID региона), значение — str (название региона).

    Returns:
        None: Функция модифицирует переданный словарь region_map на месте.

    Пример использования:
        >>> tree = [
        ...     {"value": "213", "label": "Москва", "children": [
        ...         {"value": "216", "label": "Зеленоград", "children": None}
        ...     ]}
        ... ]
        >>> region_map = {}
        >>> parse_region_tree(tree, region_map)
        >>> print(region_map)
        {213: 'Москва', 216: 'Зеленоград'}
    """
    if isinstance(node, dict):
        if "value" in node and "label" in node:
            region_map[int(node["value"])] = node["label"]  # ID приводим к int
        if "children" in node and node["children"]:
            for child in node["children"]:
                parse_region_tree(child, region_map)
    elif isinstance(node, list):
        for item in node:
            parse_region_tree(item, region_map)
