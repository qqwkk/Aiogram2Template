from aiogram import Dispatcher

from bot.decorators.admin import admin_required, admin_required_callback
from bot.functions.admin import *
from bot.configs.fsm import *

def register_handlers(dp: Dispatcher):
    # dp.register_message_handler(
    #     admin_required(admin_panel),
    #     commands=["admin"],
    #     state="*"
    # )
    pass