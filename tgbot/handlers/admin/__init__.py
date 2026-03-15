from aiogram import Dispatcher, F
from aiogram.filters import Command

from . import panel
from . import users
from . import cities
from . import broadcast
from tgbot.filters.role import AdminFilter


def register_admin_handlers(dp: Dispatcher):
    """Регистрация хендлеров администратора"""
    
    # Команды администратора
    dp.message.register(panel.cmd_admin, Command("admin"), AdminFilter())
    dp.message.register(panel.cmd_stats, Command("stats"), AdminFilter())
    
    # Обработчики текстовых сообщений
    dp.message.register(panel.show_admin_panel, F.text == "👥 Пользователи", AdminFilter())
    dp.message.register(panel.show_admin_panel, F.text == "🏙 Города", AdminFilter())
    dp.message.register(panel.show_admin_panel, F.text == "📊 Статистика", AdminFilter())
    dp.message.register(panel.show_admin_panel, F.text == "📢 Рассылка", AdminFilter())
    
    # Callback-хендлеры
    dp.callback_query.register(users.process_users_panel, F.data.startswith("admin:users"))
    dp.callback_query.register(cities.process_cities_panel, F.data.startswith("admin:cities"))
    dp.callback_query.register(panel.process_stats, F.data.startswith("admin:stats"))
    dp.callback_query.register(broadcast.process_broadcast, F.data.startswith("admin:broadcast"))