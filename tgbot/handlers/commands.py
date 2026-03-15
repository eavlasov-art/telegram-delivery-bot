from aiogram import Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from tgbot.keyboards.default import get_main_keyboard
from tgbot.services.database import UserRepository


async def cmd_start(message: Message, user_repo: UserRepository, role: str):
    """Обработчик команды /start"""
    user = message.from_user
    
    # Регистрируем пользователя
    db_user = await user_repo.create_user(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name
    )
    
    # Приветственное сообщение в зависимости от роли
    welcome_texts = {
        "admin": "👑 Добро пожаловать, администратор!",
        "partner": "🤝 Добро пожаловать, партнер!",
        "manager": "📊 Добро пожаловать, менеджер!",
        "courier": "🚚 Добро пожаловать, курьер!",
        "customer": "🛍 Добро пожаловать, заказчик!"
    }
    
    text = welcome_texts.get(role, "👋 Добро пожаловать!")
    text += "\n\nИспользуйте меню для навигации."
    
    await message.answer(
        text,
        reply_markup=get_main_keyboard(role)
    )


async def cmd_help(message: Message):
    """Обработчик команды /help"""
    help_text = """
<b>📚 Доступные команды:</b>

/start - Запустить бота
/help - Показать эту справку
/profile - Мой профиль
/orders - Мои заказы
/support - Связаться с поддержкой

Для администраторов:
/admin - Панель администратора
/stats - Статистика
"""
    await message.answer(help_text)


async def cmd_profile(message: Message, user_repo: UserRepository, user: dict):
    """Обработчик команды /profile"""
    profile_text = f"""
<b>👤 Ваш профиль:</b>

🆔 ID: {user['user_id']}
📝 Имя: {user['full_name']}
📞 Username: @{user['username'] or 'не указан'}
👑 Роль: {user['role']}
📅 Зарегистрирован: {user['created_at'].strftime('%d.%m.%Y')}
"""
    await message.answer(profile_text)


def register_commands(dp: Dispatcher):
    """Регистрация команд"""
    dp.message.register(cmd_start, CommandStart())
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_profile, Command("profile"))