from aiogram import Dispatcher

from .admin import register_admin_handlers
from .courier import register_courier_handlers
from .customer import register_customer_handlers
from .manager import register_manager_handlers
from .groups import register_group_handlers
from .commands import register_commands
from tgbot.dialogs import register_dialogs


def register_all_handlers(dp: Dispatcher):
    """Регистрация всех хендлеров"""
    register_commands(dp)
    register_admin_handlers(dp)
    register_manager_handlers(dp)
    register_courier_handlers(dp)
    register_customer_handlers(dp)
    register_group_handlers(dp)
    register_dialogs(dp)  # Добавляем диалоги