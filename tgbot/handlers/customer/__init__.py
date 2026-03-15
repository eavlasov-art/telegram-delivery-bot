from aiogram import Dispatcher, F
from aiogram.filters import Command

# Импортируем из созданных файлов
from .orders import cmd_orders, new_order, my_orders, order_details, cancel_order
from .profile import show_profile, edit_profile

from tgbot.filters.role import IsCustomer


def register_customer_handlers(dp: Dispatcher):
    """Регистрация хендлеров заказчика"""
    
    # Команды
    dp.message.register(cmd_orders, Command("orders"), IsCustomer())
    
    # Текстовые команды
    dp.message.register(new_order, F.text == "📦 Новый заказ", IsCustomer())
    dp.message.register(my_orders, F.text == "📋 Мои заказы", IsCustomer())
    dp.message.register(show_profile, F.text == "👤 Профиль", IsCustomer())
    
    # Callback-хендлеры
    dp.callback_query.register(order_details, F.data.startswith("order_details:"))
    dp.callback_query.register(cancel_order, F.data.startswith("order_cancel:"))