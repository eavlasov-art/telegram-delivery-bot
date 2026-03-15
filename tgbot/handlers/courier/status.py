from aiogram.types import Message

from tgbot.services.database import UserRepository


async def set_status(message: Message):
    """Команда для смены статуса"""
    await message.answer(
        "Выберите ваш текущий статус:\n"
        "🟢 Свободен - готов принимать заказы\n"
        "🔴 Занят - временно не принимаю заказы"
    )


async def set_free(message: Message, user_repo: UserRepository):
    """Установить статус 'Свободен'"""
    await message.answer("✅ Статус обновлен: вы свободны!")


async def set_busy(message: Message, user_repo: UserRepository):
    """Установить статус 'Занят'"""
    await message.answer("⏸ Статус обновлен: вы заняты")