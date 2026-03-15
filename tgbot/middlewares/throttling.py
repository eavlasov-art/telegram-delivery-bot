import time
from typing import Callable, Dict, Any, Awaitable
from collections import defaultdict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from aiogram.exceptions import AiogramError


class ThrottlingMiddleware(BaseMiddleware):
    """Middleware для ограничения частоты запросов"""
    
    def __init__(self, rate_limit: float = 0.5):
        self.rate_limit = rate_limit
        self.users_last_time = defaultdict(float)
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Определяем user_id
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        else:
            return await handler(event, data)
        
        # Проверяем время последнего запроса
        current_time = time.time()
        last_time = self.users_last_time[user_id]
        
        if current_time - last_time < self.rate_limit:
            # Слишком часто
            return
        
        self.users_last_time[user_id] = current_time
        
        try:
            return await handler(event, data)
        except AiogramError:
            # Игнорируем ошибки API
            pass