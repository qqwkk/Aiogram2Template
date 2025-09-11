from aiogram import Dispatcher

from bot.handlers.admin import register_handlers as register_admin_handlers
from bot.handlers.dev import register_handlers as register_dev_handlers
from bot.handlers.user import register_handlers as register_user_handlers

def register_all_handlers(dp: Dispatcher):
    register_user_handlers(dp)
    register_dev_handlers(dp)
    register_admin_handlers(dp)