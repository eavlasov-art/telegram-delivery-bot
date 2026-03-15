from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hbold

from tgbot.keyboards.inline import get_pagination_keyboard
from tgbot.services.database import OrderRepository


async def all_orders(message: Message, order_repo: OrderRepository):
    """Показать все заказы"""
    orders = await order_repo.get_all_orders(limit=10)
    
    if not orders:
        await message.answer("Заказов пока нет")
        return
    
    text = f"{hbold('📊 Все заказы:')}\n\n"
    
    for order in orders:
        status_emoji = {
            "pending": "⏳",
            "confirmed": "✅",
            "assigned": "👤",
            "delivering": "🚚",
            "delivered": "📦",
            "cancelled": "❌"
        }.get(order['status'], "📝")
        
        text += f"{status_emoji} Заказ #{order['id']} | {order['created_at'].strftime('%d.%m %H:%M')}\n"
        text += f"   👤 Клиент: {order['customer_name']}\n"
        text += f"   🚚 Курьер: {order['courier_name'] or 'не назначен'}\n"
        text += f"   💰 {order['price']} ₽\n\n"
    
    await message.answer(
        text,
        reply_markup=get_pagination_keyboard("orders", 1, 1)
    )


async def order_details_manager(callback: CallbackQuery, order_repo: OrderRepository):
    """Детали заказа для менеджера"""
    order_id = int(callback.data.split(":")[1])
    order = await order_repo.get_order_full(order_id)
    
    if not order:
        await callback.answer("Заказ не найден")
        return
    
    text = f"""
{hbold(f'📦 Заказ #{order["id"]}')}

👤 Клиент: {order['customer_name']} (@{order['customer_username']})
📞 Телефон: {order['customer_phone']}
📍 Откуда: {order['pickup_address']}
🏁 Куда: {order['delivery_address']}
📝 Описание: {order['description']}
📊 Статус: {order['status']}
🚚 Курьер: {order['courier_name'] or 'не назначен'}
💰 Стоимость: {order['price']} ₽
💳 Оплата: {order['payment_method']}
📅 Создан: {order['created_at'].strftime('%d.%m.%Y %H:%M')}
"""
    
    await callback.message.edit_text(text)
    await callback.answer()