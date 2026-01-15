# -*- coding: utf-8 -*-
from aiogram.fsm.state import StatesGroup, State


class AnalysisState(StatesGroup):
    link_post = State()


class ChooseWinnerState(StatesGroup):
    waiting_for_link = State()
