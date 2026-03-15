import asyncio
import logging
from pathlib import Path


from tgbot.config import settings
import os

# ОТЛАДКА
print("=== ЗАПУСК БОТА ===")
print(f"1. ADMIN_IDS из os.environ: {os.environ.get('ADMIN_IDS')}")
print(f"2. settings.ADMIN_IDS (сырое): {settings.ADMIN_IDS}")
print(f"3. settings.bot.admin_ids (после парсинга): {settings.bot.admin_ids}")
print("=" * 30)


from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram_dialog import setup_dialogs
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from redis.asyncio import Redis

from tgbot.config import settings
from tgbot.dialogs import register_dialogs
from tgbot.handlers import register_all_handlers
from tgbot.middlewares import register_all_middlewares
from tgbot.services.database import create_db_pool
from tgbot.services.scheduler import setup_scheduler
from tgbot.utils.logging import setup_logging

logger = logging.getLogger(__name__)


async def setup_storage() -> tuple[MemoryStorage | RedisStorage, Redis | None]:
    """Настройка хранилища FSM"""
    if settings.redis.use_redis:
        redis = Redis.from_url(
            settings.redis.dsn,
            encoding="utf-8",
            decode_responses=True
        )
        storage = RedisStorage(
            redis=redis,
            key_builder=DefaultKeyBuilder(with_destiny=True)
        )
        return storage, redis
    return MemoryStorage(), None


async def on_startup(bot: Bot, scheduler: AsyncIOScheduler = None):
    """Действия при запуске бота"""
    logger.info("Бот запущен")
    
    # Установка команд меню
    from tgbot.keyboards.commands import set_default_commands
    await set_default_commands(bot)
    
    # Запуск планировщика если нужно
    if scheduler and settings.scheduler.enabled:
        scheduler.start()
        logger.info("Планировщик задач запущен")


async def on_shutdown(bot: Bot, pool, redis_client: Redis = None):
    """Действия при остановке бота"""
    logger.info("Бот останавливается")
    
    # Закрытие соединений
    await bot.session.close()
    await pool.close()
    
    if redis_client:
        await redis_client.close()
    
    logger.info("Бот остановлен")


async def main():
    """Главная функция запуска бота"""
    # Настройка логирования
    setup_logging()
    
    logger.info("Запуск бота...")
    logger.info(f"Режим работы: {settings.BOT_MODE.value}")
    logger.info(f"Использование Redis: {settings.redis.use_redis}")
    
    # Создание хранилища
    storage, redis_client = await setup_storage()
    
    # Создание пула соединений с БД
    pool = await create_db_pool(settings.db)
    logger.info("Подключение к БД установлено")
    
    # Инициализация бота
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Инициализация диспетчера
    dp = Dispatcher(storage=storage)
    
    # Регистрация мидлварей
    register_all_middlewares(dp, pool)
    
    # Регистрация фильтров
    from tgbot.filters import register_all_filters
    register_all_filters(dp)
    
    # Регистрация хендлеров
    register_all_handlers(dp)
    
    # Регистрация диалогов
    register_dialogs(dp)
    setup_dialogs(dp)
    
    # Настройка планировщика
    scheduler = await setup_scheduler(bot, pool) if settings.scheduler.enabled else None
    
    # Передача зависимостей в диспетчер
    dp.workflow_data.update({
        "pool": pool,
        "redis": redis_client,
        "scheduler": scheduler,
        "config": settings
    })
    
    try:
        # Запуск бота
        if settings.BOT_MODE.value == "webhook" and settings.webhook.url:
            # Режим вебхуков
            await bot.set_webhook(
                url=settings.webhook.url,
                allowed_updates=dp.resolve_used_update_types(),
                drop_pending_updates=settings.bot.skip_updates,
                max_connections=settings.webhook.max_connections
            )
            logger.info(f"Вебхук установлен на {settings.webhook.url}")
            
            # Запуск веб-сервера
            from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
            from aiohttp import web
            
            app = web.Application()
            webhook_requests_handler = SimpleRequestHandler(
                dispatcher=dp,
                bot=bot,
            )
            webhook_requests_handler.register(app, path=settings.webhook.path)
            setup_application(app, dp, bot=bot)
            
            await on_startup(bot, scheduler)
            runner = web.AppRunner(app)
            await runner.setup()
            await web.TCPSite(
                runner,
                host=settings.webhook.host,
                port=settings.webhook.port
            ).start()
            
            # Ожидание остановки
            await asyncio.Event().wait()
            
        else:
            # Режим поллинга
            await on_startup(bot, scheduler)
            await dp.start_polling(
                bot,
                allowed_updates=dp.resolve_used_update_types(),
                drop_pending_updates=settings.bot.skip_updates
            )
    finally:
        await on_shutdown(bot, pool, redis_client)


if __name__ == "__main__":
    asyncio.run(main())