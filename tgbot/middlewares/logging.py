import time
from typing import Callable, Dict, Any, Awaitable
import logging

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update, Message, CallbackQuery

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Middleware для логирования всех действий"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        start_time = time.time()
        
        # Логируем входящее событие
        if isinstance(event, Update):
            if event.message:
                user = event.message.from_user
                text = event.message.text or event.message.caption or "[нет текста]"
                logger.info(
                    f"📩 Сообщение от {user.full_name} (@{user.username}, id={user.id}): {text[:100]}"
                )
            elif event.callback_query:
                user = event.callback_query.from_user
                data_cb = event.callback_query.data
                logger.info(
                    f"🔄 Callback от {user.full_name} (@{user.username}, id={user.id}): {data_cb}"
                )
        
        result = await handler(event, data)
        
        # Логируем время выполнения
        duration = time.time() - start_time
        if duration > 1.0:  # Логируем медленные запросы
            logger.warning(f"⚠️ Медленный запрос ({duration:.2f} сек)")
        
        return result