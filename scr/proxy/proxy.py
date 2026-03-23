# -*- coding: utf-8 -*-
import os


def setup_proxy(user_proxy, password_proxy, ip_proxy, port_proxy):
    """
    Настраивает прокси для HTTP и HTTPS
    :param user_proxy: логин для аутентификации на прокси
    :param password_proxy: пароль для аутентификации на прокси
    :param ip_proxy: IP-адрес прокси-сервера
    :param port_proxy: порт прокси-сервера
    """
    # Указываем прокси для HTTP и HTTPS
    os.environ['http_proxy'] = f"http://{user_proxy}:{password_proxy}@{ip_proxy}:{port_proxy}"
    os.environ['https_proxy'] = f"http://{user_proxy}:{password_proxy}@{ip_proxy}:{port_proxy}"
