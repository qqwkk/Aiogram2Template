from functools import wraps
from bot.databases.postgres import User, Admin
from datetime import datetime
from aiogram.types import Message, CallbackQuery
from loguru import logger

def admin_required(func):
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        user_id = message.from_user.id
        from_user = message.from_user
        try:
            users_id = await User.select_id(user_id)
            if not users_id:
                await User.insert(
                    user_id,
                    from_user.username,
                    from_user.first_name,
                    from_user.last_name,
                    from_user.language_code,
                    from_user.is_premium
                )
                users_id = await User.select_id(user_id)

            admin = await Admin.select_id(users_id)
            if not admin:
                return await message.answer(
                    '🚫 <b>У вас нет доступа</b>\nВы не являетесь администратором.',
                    parse_mode='html'
                )

            return await func(message, *args, **kwargs)

        except Exception as e:
            logger.error(e)
            await message.answer(
                '🚫 <b>Произошла ошибка при проверке прав доступа</b>.',
                parse_mode='html'
            )

    return wrapper

def admin_required_callback(func):
    @wraps(func)
    async def wrapper(callback: CallbackQuery, *args, **kwargs):
        user_id = callback.from_user.id
        from_user = callback.from_user

        try:
            users_id = await User.select_id(user_id)
            if not users_id:
                await User.insert(
                    user_id,
                    from_user.username,
                    from_user.first_name,
                    from_user.last_name,
                    from_user.language_code,
                    from_user.is_premium
                )
                users_id = await User.select_id(user_id)

            admin = await Admin.select_id(users_id)
            if not admin:
                return await callback.answer(
                    '🚫 У вас нет доступа\nВы не являетесь администратором',
                    show_alert=True
                )

            return await func(callback, *args, **kwargs)

        except Exception as e:
            logger.error(e)
            await callback.answer(
                '🚫 <b>Произошла ошибка при проверке прав доступа</b>.',
                show_alert=True
            )

    return wrapper