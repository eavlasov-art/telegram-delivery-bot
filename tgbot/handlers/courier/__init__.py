from aiogram import Dispatcher, F
from aiogram.filters import Command

# Импортируем конкретные функции, а не модули
from .orders import available_orders, my_orders, take_order, order_route, complete_order
from .profile import show_profile
from .status import set_status, set_free, set_busy

from tgbot.filters.role import IsCourier


def register_courier_handlers(dp: Dispatcher):
    """Регистрация хендлеров курьера"""
    
    # Команды
    dp.message.register(available_orders, Command("available_orders"), IsCourier())
    dp.message.register(my_orders, Command("my_orders"), IsCourier())
    dp.message.register(set_status, Command("status"), IsCourier())
    
    # Текстовые команды
    dp.message.register(available_orders, F.text == "🚚 Доступные заказы", IsCourier())
    dp.message.register(my_orders, F.text == "✅ Мои заказы", IsCourier())
    dp.message.register(set_free, F.text == "🟢 Свободен", IsCourier())
    dp.message.register(set_busy, F.text == "🔴 Занят", IsCourier())
    dp.message.register(show_profile, F.text == "👤 Профиль", IsCourier())
    
    # Callback-хендлеры
    dp.callback_query.register(take_order, F.data.startswith("order_take:"))
    dp.callback_query.register(order_route, F.data.startswith("order_route:"))
    dp.callback_query.register(complete_order, F.data.startswith("order_complete:"))