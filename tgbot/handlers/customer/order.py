from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from tgbot.keyboards.default import get_cancel_keyboard, get_location_keyboard
from tgbot.keyboards.inline import get_order_keyboard


class OrderCreation(StatesGroup):
    """Состояния создания заказа"""
    choosing_type = State()
    entering_description = State()
    choosing_pickup = State()
    choosing_delivery = State()
    confirming = State()


async def new_order(message: Message, state: FSMContext):
    """Начать создание нового заказа"""
    await state.set_state(OrderCreation.choosing_type)
    await message.answer(
        "📦 <b>Создание нового заказа</b>\n\n"
        "Выберите тип заказа:",
        reply_markup=get_order_type_keyboard()
    )


async def my_orders(message: Message, order_repo):
    """Показать список заказов пользователя"""
    orders = await order_repo.get_user_orders(message.from_user.id)
    
    if not orders:
        await message.answer("У вас пока нет заказов")
        return
    
    text = "<b>📋 Ваши заказы:</b>\n\n"
    
    for order in orders[:5]:
        status_emoji = {
            "pending": "⏳",
            "confirmed": "✅",
            "delivering": "🚚",
            "delivered": "📦",
            "cancelled": "❌"
        }.get(order['status'], "📝")
        
        text += f"{status_emoji} Заказ #{order['id']}\n"
        text += f"   Статус: {order['status']}\n"
        text += f"   Откуда: {order['pickup_address'][:30]}...\n"
        text += f"   Куда: {order['delivery_address'][:30]}...\n\n"
    
    await message.answer(text)


async def order_details(callback: CallbackQuery, order_repo):
    """Показать детали заказа"""
    order_id = int(callback.data.split(":")[1])
    order = await order_repo.get_order(order_id)
    
    if not order:
        await callback.message.answer("Заказ не найден")
        return
    
    text = f"""
<b>📦 Заказ #{order['id']}</b>

📝 Описание: {order['description']}
📍 Откуда: {order['pickup_address']}
🏁 Куда: {order['delivery_address']}
📊 Статус: {order['status']}
👤 Курьер: {order['courier_name'] or 'не назначен'}
💰 Стоимость: {order['price']} ₽
📅 Создан: {order['created_at'].strftime('%d.%m.%Y %H:%M')}
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_order_keyboard(order_id, "customer", order['status'])
    )
    await callback.answer()


async def cancel_order(callback: CallbackQuery, order_repo):
    """Отменить заказ"""
    order_id = int(callback.data.split(":")[2])
    
    # Проверяем, можно ли отменить
    order = await order_repo.get_order(order_id)
    
    if order['status'] not in ['pending', 'confirmed']:
        await callback.answer("❌ Этот заказ уже нельзя отменить", show_alert=True)
        return
    
    # Отменяем заказ
    await order_repo.update_status(order_id, "cancelled")
    
    await callback.message.edit_text(
        "✅ Заказ успешно отменен"
    )
    await callback.answer("Заказ отменен")