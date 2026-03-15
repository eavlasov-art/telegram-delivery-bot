from aiogram.types import Message

from tgbot.services.database import UserRepository


async def show_profile(message: Message, user_repo: UserRepository):
    """Показать профиль курьера"""
    # Заглушка для демонстрации
    await message.answer(
        "👤 <b>Профиль курьера</b>\n\n"
        "Функционал в разработке"
    )