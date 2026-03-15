from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext



async def show_users_list(message: Message):
    """Показать список пользователей"""
    # Заглушка для демонстрации
    await message.answer(
        "👥 <b>Управление пользователями</b>\n\n"
        "Функционал в разработке"
    )


async def process_users_panel(callback: CallbackQuery):
    """Обработка панели пользователей"""
    await callback.answer("Раздел пользователей")


async def change_user_role(callback: CallbackQuery):
    """Изменение роли пользователя"""
    await callback.answer("Функция изменения роли")