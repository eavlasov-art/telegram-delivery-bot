from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
import asyncpg

from tgbot.services.database import UserRepository, OrderRepository


class DbMiddleware(BaseMiddleware):
    """Middleware для передачи пула соединений с БД"""
    
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        async with self.pool.acquire() as conn:
            # Передаем коннект и репозитории в хендлер
            data["conn"] = conn
            data["user_repo"] = UserRepository(conn)
            data["order_repo"] = OrderRepository(conn)
            
            # Для обратной совместимости с старым кодом
            data["db_conn"] = conn
            
            return await handler(event, data)