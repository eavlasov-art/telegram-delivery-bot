from aiogram.types import Message
from aiogram.filters import Command

from tgbot.services.database import UserRepository


async def set_status(message: Message, user_repo: UserRepository):
    """Команда для смены статуса"""
    await message.answer(
        "Выберите ваш текущий статус:\n"
        "🟢 Свободен - готов принимать заказы\n"
        "🔴 Занят - временно не принимаю заказы\n"
        "🚚 На заказе - автоматически устанавливается"
    )


async def set_free(message: Message, user_repo: UserRepository):
    """Установить статус 'Свободен'"""
    await user_repo.update_courier_status(message.from_user.id, "free")
    await message.answer(
        "✅ Статус обновлен: вы свободны и готовы принимать заказы!"
    )


async def set_busy(message: Message, user_repo: UserRepository):
    """Установить статус 'Занят'"""
    await user_repo.update_courier_status(message.from_user.id, "busy")
    await message.answer(
        "⏸ Статус обновлен: вы заняты. Заказы не будут поступать."
    )