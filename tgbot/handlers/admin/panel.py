from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from tgbot.keyboards.inline import get_admin_panel_keyboard
from tgbot.services.database import UserRepository


async def cmd_admin(message: Message):
    """Команда /admin - открыть админ-панель"""
    await message.answer(
        "👑 <b>Панель администратора</b>\n\n"
        "Выберите раздел для управления:",
        reply_markup=get_admin_panel_keyboard()
    )


async def cmd_stats(message: Message, user_repo: UserRepository):
    """Команда /stats - быстрая статистика"""
    # Получаем статистику
    total_users = await user_repo.get_total_users()
    users_by_role = await user_repo.get_users_by_role()
    
    stats_text = f"""
📊 <b>Общая статистика:</b>

👥 Всего пользователей: {total_users}

По ролям:
• 👑 Администраторы: {users_by_role.get('admin', 0)}
• 🤝 Партнеры: {users_by_role.get('partner', 0)}
• 📊 Менеджеры: {users_by_role.get('manager', 0)}
• 🚚 Курьеры: {users_by_role.get('courier', 0)}
• 🛍 Заказчики: {users_by_role.get('customer', 0)}
"""
    await message.answer(stats_text)


async def show_admin_panel(message: Message):
    """Показать соответствующий раздел админ-панели"""
    text = message.text
    
    if text == "👥 Пользователи":
        from .users import show_users_list
        await show_users_list(message)
    elif text == "🏙 Города":
        from .cities import show_cities_list
        await show_cities_list(message)
    elif text == "📊 Статистика":
        await show_detailed_stats(message)
    elif text == "📢 Рассылка":
        from .broadcast import start_broadcast
        await start_broadcast(message)


async def show_detailed_stats(message: Message, user_repo: UserRepository):
    """Показать детальную статистику"""
    # Детальная статистика по дням
    daily_stats = await user_repo.get_daily_stats()
    
    stats_text = "<b>📊 Детальная статистика:</b>\n\n"
    
    for day in daily_stats[:7]:  # Последние 7 дней
        stats_text += f"{day['date']}: +{day['new_users']} новых\n"
    
    await message.answer(stats_text)


async def process_stats(callback: CallbackQuery):
    """Обработка callback для статистики"""
    await callback.answer()
    # Логика обработки