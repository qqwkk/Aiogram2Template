from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext

from bot.keyboards.user import *

async def start(message: Message):
    await message.answer("Hello World")