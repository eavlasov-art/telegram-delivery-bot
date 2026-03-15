from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from tgbot.services.database import CityRepository


async def show_cities_list(message: Message):
    """Показать список городов"""
    # Заглушка для демонстрации
    await message.answer(
        "🏙 <b>Управление городами</b>\n\n"
        "Функционал в разработке"
    )


async def process_cities_panel(callback: CallbackQuery):
    """Обработка панели городов"""
    await callback.answer("Раздел городов")