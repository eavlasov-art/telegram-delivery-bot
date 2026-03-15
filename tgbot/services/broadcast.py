import asyncio
import logging
from typing import Union, List

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramRetryAfter, TelegramForbiddenError
from aiogram.types import Message

logger = logging.getLogger(__name__)


async def send_message(
    bot: Bot,
    user_id: int,
    text: str,
    photo: Union[str, None] = None,
    disable_notification: bool = False
) -> bool:
    """
    Безопасная отправка сообщения пользователю
    Возвращает True если успешно, False если ошибка
    """
    try:
        if photo:
            await bot.send_photo(
                chat_id=user_id,
                photo=photo,
                caption=text,
                disable_notification=disable_notification
            )
        else:
            await bot.send_message(
                chat_id=user_id,
                text=text,
                disable_notification=disable_notification
            )
        return True
        
    except TelegramRetryAfter as e:
        logger.warning(f"Flood limit exceeded for user {user_id}. Retry after {e.retry_after} seconds")
        await asyncio.sleep(e.retry_after)
        return await send_message(bot, user_id, text, photo, disable_notification)
        
    except TelegramForbiddenError:
        logger.info(f"User {user_id} blocked the bot")
        return False
        
    except TelegramAPIError as e:
        logger.error(f"Telegram API error for user {user_id}: {e}")
        return False
        
    except Exception as e:
        logger.error(f"Unexpected error for user {user_id}: {e}")
        return False


async def broadcast(
    bot: Bot,
    users: List[dict],
    text: str,
    photo: Union[str, None] = None,
    delay: float = 0.05  # Задержка между сообщениями для избежания флуда
) -> tuple[int, int]:
    """
    Массовая рассылка сообщений пользователям
    
    Returns:
        tuple[int, int]: (количество успешных, количество ошибок)
    """
    sent = 0
    failed = 0
    
    for user in users:
        if await send_message(bot, user['user_id'], text, photo):
            sent += 1
        else:
            failed += 1
            
        # Задержка между сообщениями
        await asyncio.sleep(delay)
        
        # Логируем прогресс каждые 100 сообщений
        if (sent + failed) % 100 == 0:
            logger.info(f"Broadcast progress: {sent} sent, {failed} failed")
    
    logger.info(f"Broadcast completed: {sent} sent, {failed} failed")
    return sent, failed