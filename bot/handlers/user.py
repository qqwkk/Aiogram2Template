from aiogram import Dispatcher

from bot.functions.user import *

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(
        start,
        commands=['start'],
        state='*'
    )