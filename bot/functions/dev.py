from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.storage import FSMContext
from pprint import pformat

class DevFunctions:
    @staticmethod
    async def get_user_id(message: Message):
        await message.answer(message.from_user.id)

    @staticmethod
    async def get_message(message: Message):
        await message.answer(message)

    @staticmethod
    async def get_message_id(message: Message):
        if message.reply_to_message:
            await message.answer(message.reply_to_message.message_id)
        else:
            await message.answer(message.message_id)

    @staticmethod
    async def debug(message_or_callback, state: FSMContext):
        if isinstance(message_or_callback, Message):
            user = message_or_callback.from_user
            chat_id = message_or_callback.chat.id
            text = message_or_callback.text
        elif isinstance(message_or_callback, CallbackQuery):
            user = message_or_callback.from_user
            chat_id = message_or_callback.message.chat.id
            text = message_or_callback.data
        else:
            return

        data = await state.get_data()
        current_state = await state.get_state()

        debug_info = (
            f"👤 <b>User:</b> {user.full_name} (@{user.username})\n"
            f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
            f"💭 <b>Chat ID:</b> <code>{chat_id}</code>\n"
            f"💬 <b>Message:</b> <code>{text}</code>\n"
            f"📦 <b>FSM State:</b> <code>{current_state}</code>\n"
            f"🧠 <b>FSM Data:</b>\n<pre>{pformat(data)}</pre>"
        )

        await message_or_callback.answer(debug_info, parse_mode="HTML")