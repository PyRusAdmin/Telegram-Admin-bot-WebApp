# -*- coding: utf-8 -*-
from aiogram.fsm.state import StatesGroup, State


class AnalysisState(StatesGroup):
    link_post = State()
