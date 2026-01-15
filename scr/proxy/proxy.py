# -*- coding: utf-8 -*-
import os


def setup_proxy(USER, PASSWORD, IP, PORT):
    # Указываем прокси для HTTP и HTTPS
    os.environ['http_proxy'] = f"http://{USER}:{PASSWORD}@{IP}:{PORT}"
    os.environ['https_proxy'] = f"http://{USER}:{PASSWORD}@{IP}:{PORT}"
