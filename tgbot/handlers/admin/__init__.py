from aiogram import Dispatcher, F
from aiogram.filters import Command

# Импортируем конкретные функции, а не модули
from .panel import cmd_admin, cmd_stats, show_admin_panel, process_stats
from .users import show_users_list, process_users_panel, change_user_role
from .cities import show_cities_list, process_cities_panel
from .broadcast import cmd_broadcast

from tgbot.filters.role import AdminFilter


def register_admin_handlers(dp: Dispatcher):
    """Регистрация хендлеров администратора"""
    
    # Команды администратора
    dp.message.register(cmd_admin, Command("admin"), AdminFilter())
    dp.message.register(cmd_stats, Command("stats"), AdminFilter())
    dp.message.register(cmd_broadcast, Command("broadcast"), AdminFilter())
    
    # Обработчики текстовых сообщений
    dp.message.register(show_admin_panel, F.text == "👥 Пользователи", AdminFilter())
    dp.message.register(show_admin_panel, F.text == "🏙 Города", AdminFilter())
    dp.message.register(show_admin_panel, F.text == "📊 Статистика", AdminFilter())
    dp.message.register(show_admin_panel, F.text == "📢 Рассылка", AdminFilter())
    
    # Callback-хендлеры
    dp.callback_query.register(process_users_panel, F.data.startswith("admin:users"))
    dp.callback_query.register(process_cities_panel, F.data.startswith("admin:cities"))
    dp.callback_query.register(process_stats, F.data.startswith("admin:stats"))
    
    # Дополнительные callback'и
    dp.callback_query.register(change_user_role, F.data.startswith("change_role:"))