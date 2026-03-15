from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from tgbot.filters.role import AdminFilter


async def cmd_broadcast(message: Message, state: FSMContext):
    """Команда для запуска рассылки"""
    await message.answer(
        "📢 <b>Рассылка</b>\n\n"
        "Функционал в разработке"
    )