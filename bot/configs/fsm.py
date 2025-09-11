from aiogram.dispatcher.filters.state import State, StatesGroup

class MainMenuState(StatesGroup):
    menu = State()

class AccountState(StatesGroup):
    menu = State()