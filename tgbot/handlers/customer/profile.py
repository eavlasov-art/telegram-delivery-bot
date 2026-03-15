from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from tgbot.services.database import UserRepository


async def show_profile(message: Message, user_repo: UserRepository):
    """Показать профиль заказчика"""
    user = message.from_user
    await message.answer(
        f"👤 <b>Ваш профиль</b>\n\n"
        f"ID: {user.id}\n"
        f"Имя: {user.full_name}\n"
        f"Username: @{user.username or 'не указан'}\n\n"
        f"Функционал в разработке"
    )


async def edit_profile(message: Message, state: FSMContext):
    """Редактировать профиль"""
    await message.answer(
        "✏️ <b>Редактирование профиля</b>\n\n"
        "Функционал в разработке"
    )