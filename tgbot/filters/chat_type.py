from typing import Union, List

from aiogram.filters import BaseFilter
from aiogram.types import Message


class ChatTypeFilter(BaseFilter):
    """Фильтр для типа чата"""
    
    def __init__(self, chat_type: Union[str, List[str]]):
        self.chat_type = [chat_type] if isinstance(chat_type, str) else chat_type
    
    async def __call__(self, message: Message) -> bool:
        return message.chat.type in self.chat_type