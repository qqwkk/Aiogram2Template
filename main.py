from loguru import logger
from aiogram import executor

from bot.configs.db_pool import create_pool
from bot.configs.databases import postgresql, r
from bot.databases.init import init_db
from bot.handlers.all import register_all_handlers
from bot.configs.bot import dp, bot
from bot.configs.commands import botcommands

async def on_startup(dp):
    logger.info("Бот запускается...")

    # 🔁 Создание пула
    await create_pool(
        user=postgresql.user,
        password=postgresql.password,
        database=postgresql.db_name,
        host=postgresql.host,
        port=postgresql.port
    )

    # 🔁 Создание таблиц
    try:
        await init_db()
        logger.info("База данных инициализирована.")
    except Exception:
        logger.error("Ошибка при инициализации базы данных:")
        raise

    register_all_handlers(dp)
    logger.info("Хендлеры зарегистрированы.")

    await bot.set_my_commands(botcommands)
    logger.info("Команды зарегистрированы.")
    
async def on_shutdown(dp):
    logger.info("🛑 Бот останавливается...")
    if r:
        r.close()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)