from aiogram import Dispatcher, F
from aiogram.filters import Command

from . import orders
from . import profile
from . import status
from tgbot.filters.role import IsCourier


def register_courier_handlers(dp: Dispatcher):
    """Регистрация хендлеров курьера"""
    
    # Команды
    dp.message.register(orders.available_orders, Command("available_orders"), IsCourier())
    dp.message.register(orders.my_orders, Command("my_orders"), IsCourier())
    dp.message.register(status.set_status, Command("status"), IsCourier())
    
    # Текстовые команды
    dp.message.register(orders.available_orders, F.text == "🚚 Доступные заказы", IsCourier())
    dp.message.register(orders.my_orders, F.text == "✅ Мои заказы", IsCourier())
    dp.message.register(status.set_free, F.text == "🟢 Свободен", IsCourier())
    dp.message.register(status.set_busy, F.text == "🔴 Занят", IsCourier())
    dp.message.register(profile.show_profile, F.text == "👤 Профиль", IsCourier())
    
    # Callback-хендлеры
    dp.callback_query.register(orders.take_order, F.data.startswith("order_take:"))
    dp.callback_query.register(orders.order_route, F.data.startswith("order_route:"))
    dp.callback_query.register(orders.complete_order, F.data.startswith("order_complete:"))