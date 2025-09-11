from aiogram import Dispatcher

from bot.decorators.admin import admin_required
from bot.functions.dev import DevFunctions

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(admin_required(DevFunctions.get_user_id), commands=['id'], state='*')
    dp.register_message_handler(admin_required(DevFunctions.get_message), commands=['message'], state='*')
    dp.register_message_handler(admin_required(DevFunctions.get_message_id), commands=['message_id'], state='*')

    dp.register_message_handler(admin_required(DevFunctions.debug), commands=['debug'], state='*')