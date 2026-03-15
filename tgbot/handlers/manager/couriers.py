from aiogram.types import Message
from aiogram.utils.markdown import hbold

from tgbot.services.database import UserRepository


async def couriers_list(message: Message, user_repo: UserRepository):
    """Показать список курьеров"""
    couriers = await user_repo.get_couriers()

    if not couriers:
        await message.answer("Курьеров пока нет")
        return

    text = f"{hbold('👥 Список курьеров:')}\n\n"

    for courier in couriers:
        text += f"ID: {courier['user_id']}\n"
        text += f"Имя: {courier['full_name']}\n"
        text += f"Статус: {courier['status']}\n\n"

    await message.answer(text)


async def assign_courier(callback_query, user_repo: UserRepository):
    """Назначить курьера на заказ"""
    # Заглушка
    await callback_query.answer("Функция в разработке")