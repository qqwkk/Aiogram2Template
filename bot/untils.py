from aiogram.types import Message, CallbackQuery
from typing import List, Union


def _get_sender(message_or_callback: Union[Message, CallbackQuery]) -> Message:
    """Вернуть Message для отправки ответов (единообразно для Message/CallbackQuery)."""
    if isinstance(message_or_callback, CallbackQuery):
        return message_or_callback.message
    return message_or_callback

def _chunk(text: str, limit: int = 3800) -> List[str]:
    """
    Порезать длинный текст на части с запасом под HTML.
    Telegram лимит ~4096, оставляем запас под теги и эмодзи.
    """
    res, cur = [], []
    cur_len = 0
    for line in text.splitlines(keepends=True):
        if cur_len + len(line) > limit:
            res.append("".join(cur))
            cur, cur_len = [line], len(line)
        else:
            cur.append(line)
            cur_len += len(line)
    if cur:
        res.append("".join(cur))
    return res