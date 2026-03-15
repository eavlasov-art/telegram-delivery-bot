import logging
from datetime import datetime, timedelta

from aiogram import Bot
import asyncpg

from tgbot.services.database import UserRepository, OrderRepository

logger = logging.getLogger(__name__)


async def send_daily_stats(bot: Bot, pool: asyncpg.Pool):
    """Отправка ежедневной статистики администраторам"""
    async with pool.acquire() as conn:
        user_repo = UserRepository(conn)
        order_repo = OrderRepository(conn)
        
        # Получаем статистику за сегодня
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        new_users = await user_repo.get_users_count_by_date(today, tomorrow)
        new_orders = await order_repo.get_orders_count_by_date(today, tomorrow)
        completed_orders = await order_repo.get_completed_orders_count(today, tomorrow)
        
        stats_text = f"""
📊 <b>Ежедневная статистика за {today.strftime('%d.%m.%Y')}</b>

👥 Новых пользователей: {new_users}
📦 Новых заказов: {new_orders}
✅ Выполнено заказов: {completed_orders}
💰 Выручка: {await order_repo.get_daily_revenue(today, tomorrow)} ₽
"""
        
        # Отправляем админам
        admins = await user_repo.get_admins()
        for admin in admins:
            try:
                await bot.send_message(admin['user_id'], stats_text)
            except Exception as e:
                logger.error(f"Не удалось отправить статистику админу {admin['user_id']}: {e}")


async def send_weekly_stats(bot: Bot, pool: asyncpg.Pool):
    """Отправка еженедельной статистики"""
    async with pool.acquire() as conn:
        user_repo = UserRepository(conn)
        order_repo = OrderRepository(conn)
        
        # Получаем статистику за неделю
        week_ago = datetime.now() - timedelta(days=7)
        
        new_users = await user_repo.get_users_count_since(week_ago)
        new_orders = await order_repo.get_orders_count_since(week_ago)
        completed_orders = await order_repo.get_completed_orders_count_since(week_ago)
        
        # Топ курьеров
        top_couriers = await order_repo.get_top_couriers(week_ago, limit=5)
        
        stats_text = f"""
📊 <b>Недельная статистика</b>
📅 {week_ago.strftime('%d.%m.%Y')} - {datetime.now().strftime('%d.%m.%Y')}

👥 Новых пользователей: {new_users}
📦 Новых заказов: {new_orders}
✅ Выполнено заказов: {completed_orders}
💰 Выручка за неделю: {await order_repo.get_weekly_revenue()} ₽

🏆 <b>Топ курьеров недели:</b>
"""
        
        for i, courier in enumerate(top_couriers, 1):
            stats_text += f"{i}. {courier['name']} - {courier['orders']} заказов\n"
        
        # Отправляем админам
        admins = await user_repo.get_admins()
        for admin in admins:
            try:
                await bot.send_message(admin['user_id'], stats_text)
            except Exception as e:
                logger.error(f"Не удалось отправить статистику админу {admin['user_id']}: {e}")


async def remind_couriers(bot: Bot, pool: asyncpg.Pool):
    """Напоминание курьерам о необходимости обновить статус"""
    async with pool.acquire() as conn:
        user_repo = UserRepository(conn)
        
        # Получаем курьеров, которые давно не обновляли статус
        inactive_couriers = await user_repo.get_inactive_couriers(hours=6)
        
        for courier in inactive_couriers:
            try:
                await bot.send_message(
                    courier['user_id'],
                    "⏰ <b>Напоминание</b>\n\n"
                    "Вы давно не обновляли свой статус.\n"
                    "Пожалуйста, укажите ваш текущий статус:\n"
                    "🟢 Свободен - готов принимать заказы\n"
                    "🔴 Занят - временно не работаю"
                )
            except Exception as e:
                logger.error(f"Не удалось отправить напоминание курьеру {courier['user_id']}: {e}")