from aiogram.types import Message, CallbackQuery

from tgbot.services.database import OrderRepository


async def available_orders(message: Message, order_repo: OrderRepository):
    """Показать доступные для взятия заказы"""
    # Заглушка для демонстрации
    await message.answer(
        "🚚 <b>Доступные заказы</b>\n\n"
        "Функционал в разработке"
    )


async def my_orders(message: Message, order_repo: OrderRepository):
    """Показать заказы, взятые курьером"""
    await message.answer(
        "✅ <b>Мои заказы</b>\n\n"
        "Функционал в разработке"
    )


async def take_order(callback: CallbackQuery):
    """Взять заказ в работу"""
    await callback.answer("Функция взятия заказа в разработке")


async def order_route(callback: CallbackQuery):
    """Показать маршрут заказа"""
    await callback.answer("Функция маршрута в разработке")


async def complete_order(callback: CallbackQuery):
    """Отметить заказ как выполненный"""
    await callback.answer("Функция завершения заказа в разработке")