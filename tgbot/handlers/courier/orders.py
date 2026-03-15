from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hbold

from tgbot.keyboards.inline import get_order_keyboard, get_confirmation_keyboard
from tgbot.services.database import OrderRepository


async def available_orders(message: Message, order_repo: OrderRepository):
    """Показать доступные для взятия заказы"""
    orders = await order_repo.get_available_orders()
    
    if not orders:
        await message.answer(
            "🚚 На данный момент нет доступных заказов.\n"
            "Как только появится новый заказ, я сообщу!"
        )
        return
    
    text = f"{hbold('📦 Доступные заказы:')}\n\n"
    
    for order in orders[:5]:
        text += f"🆔 Заказ #{order['id']}\n"
        text += f"📍 Откуда: {order['pickup_address'][:50]}...\n"
        text += f"🏁 Куда: {order['delivery_address'][:50]}...\n"
        text += f"💰 Оплата: {order['price']} ₽\n"
        text += f"📏 Расстояние: {order['distance']} км\n"
        text += "-" * 20 + "\n"
    
    await message.answer(text)


async def my_orders(message: Message, order_repo: OrderRepository):
    """Показать заказы, взятые курьером"""
    courier_id = message.from_user.id
    orders = await order_repo.get_courier_orders(courier_id)
    
    if not orders:
        await message.answer("У вас пока нет взятых заказов")
        return
    
    text = f"{hbold('✅ Мои заказы:')}\n\n"
    
    for order in orders:
        status_emoji = {
            "assigned": "🟡",
            "delivering": "🚚",
            "delivered": "✅"
        }.get(order['status'], "📦")
        
        text += f"{status_emoji} Заказ #{order['id']}\n"
        text += f"📍 {order['pickup_address']} → {order['delivery_address']}\n"
        text += f"⏱ Время: {order['created_at'].strftime('%H:%M')}\n\n"
    
    await message.answer(text)


async def take_order(callback: CallbackQuery, order_repo: OrderRepository):
    """Взять заказ в работу"""
    order_id = int(callback.data.split(":")[1])
    courier_id = callback.from_user.id
    
    # Проверяем, свободен ли заказ
    order = await order_repo.get_order(order_id)
    
    if order['status'] != 'pending':
        await callback.answer("❌ Этот заказ уже взят другим курьером", show_alert=True)
        return
    
    # Назначаем курьера
    await order_repo.assign_courier(order_id, courier_id)
    
    await callback.message.edit_text(
        f"✅ Заказ #{order_id} успешно взят!\n\n"
        f"Свяжитесь с клиентом для уточнения деталей.",
        reply_markup=get_order_keyboard(order_id, "courier")
    )
    await callback.answer("Заказ принят!")


async def order_route(callback: CallbackQuery):
    """Показать маршрут заказа"""
    order_id = callback.data.split(":")[1]
    
    # Здесь можно отправить карту или ссылку на навигатор
    await callback.message.answer(
        f"📍 Маршрут для заказа #{order_id}\n"
        f"Яндекс.Карты: https://yandex.ru/maps/?rtext=~&rtt=auto\n"
        f"Google Maps: https://www.google.com/maps/dir/"
    )
    await callback.answer()


async def complete_order(callback: CallbackQuery, order_repo: OrderRepository):
    """Отметить заказ как выполненный"""
    order_id = int(callback.data.split(":")[1])
    
    await order_repo.update_status(order_id, "delivered")
    
    await callback.message.edit_text(
        f"✅ Заказ #{order_id} отмечен как выполненный!\n"
        f"Спасибо за работу!"
    )
    await callback.answer("Заказ выполнен")