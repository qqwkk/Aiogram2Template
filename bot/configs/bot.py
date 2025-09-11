import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from bot.configs.databases import redis
load_dotenv()

# Bot settings
BOT_TOKEN = os.getenv('API_TOKEN')

bot = Bot(token=BOT_TOKEN)
storage = RedisStorage2(
    host=redis.host,
    port=redis.port,
    db=redis.db,
)

dp = Dispatcher(bot, storage=storage)