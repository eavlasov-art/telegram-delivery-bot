from typing import Callable, Dict, Any, Awaitable, Optional

from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, Message, CallbackQuery
from aiogram.exceptions import TelegramAPIError


class SupportMiddleware(BaseMiddleware):
    """Middleware для пересылки сообщений в поддержку"""
    
    def __init__(self, support_chat_id: Optional[int] = None):
        self.support_chat_id = support_chat_id
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        result = await handler(event, data)
        
        # Если это сообщение и оно не обработано, пересылаем в поддержку
        if isinstance(event, Message) and self.support_chat_id:
            # Проверяем, было ли сообщение обработано
            # Для этого можно проверить, есть ли ответ в result или использовать кастомный флаг
            if not result:  # Упрощенная логика
                try:
                    bot: Bot = data.get("bot")
                    if bot:
                        await bot.forward_message(
                            chat_id=self.support_chat_id,
                            from_chat_id=event.chat.id,
                            message_id=event.message_id
                        )
                except TelegramAPIError:
                    pass
        
        return result