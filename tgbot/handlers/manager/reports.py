from aiogram.types import Message
from aiogram.utils.markdown import hbold

from tgbot.services.database import OrderRepository, OrderStatus


async def daily_report(message: Message, order_repo: OrderRepository):
    """Показать ежедневный отчет"""
    # Пример простой статистики
    total_orders = await order_repo.get_orders_count()
    pending_orders = await order_repo.get_orders_count(status=OrderStatus.PENDING)
    completed_orders = await order_repo.get_orders_count(status=OrderStatus.DELIVERED)

    text = f"{hbold('📈 Ежедневный отчет:')}\n\n"
    text += f"Всего заказов: {total_orders}\n"
    text += f"Ожидающих: {pending_orders}\n"
    text += f"Выполненных: {completed_orders}\n"

    await message.answer(text)


async def view_report(callback_query):
    """Просмотр отчета"""
    # Заглушка
    await callback_query.answer("Функция в разработке")