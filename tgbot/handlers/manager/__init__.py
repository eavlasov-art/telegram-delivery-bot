from aiogram import Dispatcher, F
from aiogram.filters import Command

from . import orders
from . import couriers
from . import reports
from tgbot.filters.role import IsManager


def register_manager_handlers(dp: Dispatcher):
    """Регистрация хендлеров менеджера"""
    
    # Команды
    dp.message.register(orders.all_orders, Command("all_orders"), IsManager())
    dp.message.register(couriers.couriers_list, Command("couriers"), IsManager())
    dp.message.register(reports.daily_report, Command("report"), IsManager())
    
    # Текстовые команды
    dp.message.register(orders.all_orders, F.text == "📊 Все заказы", IsManager())
    dp.message.register(couriers.couriers_list, F.text == "👥 Курьеры", IsManager())
    dp.message.register(reports.generate_report, F.text == "📈 Отчеты", IsManager())
    
    # Callback-хендлеры
    dp.callback_query.register(orders.order_details_manager, F.data.startswith("manager_order:"))
    dp.callback_query.register(couriers.assign_courier, F.data.startswith("assign_courier:"))
    dp.callback_query.register(reports.view_report, F.data.startswith("report:"))