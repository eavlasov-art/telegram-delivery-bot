from typing import Callable, Dict, Any, Awaitable, Optional

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update, Message, CallbackQuery

from tgbot.services.database import UserRepository


class RoleMiddleware(BaseMiddleware):
    """Middleware для определения роли пользователя"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Получаем user_id из разных типов событий
        user_id = None
        if isinstance(event, Update):
            if event.message:
                user_id = event.message.from_user.id
            elif event.callback_query:
                user_id = event.callback_query.from_user.id
        elif isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        
        if user_id and "conn" in data:
            # Получаем роль пользователя из БД
            user_repo = UserRepository(data["conn"])
            user = await user_repo.get_user(user_id)
            
            if user:
                data["role"] = user.get("role", "customer")
                data["user"] = user
            else:
                data["role"] = "unknown"
        
        return await handler(event, data)