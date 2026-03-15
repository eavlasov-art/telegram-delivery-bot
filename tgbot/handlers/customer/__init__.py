from aiogram import Dispatcher, F
from aiogram.filters import Command

from . import orders
from . import profile
from tgbot.filters.role import IsCustomer


def register_customer_handlers(dp: Dispatcher):
    """Регистрация хендлеров заказчика"""
    
    # Заказы
    dp.message.register(orders.cmd_orders, Command("orders"), IsCustomer())
    dp.message.register(orders.new_order, F.text == "📦 Новый заказ", IsCustomer())
    dp.message.register(orders.my_orders, F.text == "📋 Мои заказы", IsCustomer())
    
    # Профиль
    dp.message.register(profile.show_profile, F.text == "👤 Профиль", IsCustomer())
    dp.message.register(profile.edit_profile, F.text == "✏️ Редактировать", IsCustomer())
    
    # Callback-хендлеры для заказов
    dp.callback_query.register(orders.order_details, F.data.startswith("order_details:"))
    dp.callback_query.register(orders.cancel_order, F.data.startswith("order_cancel:"))