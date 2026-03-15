from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from tgbot.keyboards.inline import get_pagination_keyboard
from tgbot.services.database import UserRepository


class UserManagement(StatesGroup):
    """Состояния для управления пользователями"""
    selecting_user = State()
    editing_role = State()
    editing_city = State()


async def show_users_list(message: Message, user_repo: UserRepository):
    """Показать список пользователей"""
    users = await user_repo.get_all_users(limit=10)
    
    if not users:
        await message.answer("Пользователей пока нет")
        return
    
    text = "<b>👥 Список пользователей:</b>\n\n"
    
    for user in users:
        text += f"• {user['full_name']} (@{user['username']}) - {user['role']}\n"
    
    await message.answer(
        text,
        reply_markup=get_pagination_keyboard("users", 1, 1)
    )


async def process_users_panel(callback: CallbackQuery, user_repo: UserRepository):
    """Обработка панели пользователей"""
    action = callback.data.split(":")[1]
    
    if action == "list":
        await show_users_list(callback.message, user_repo)
    elif action == "search":
        await callback.message.answer("Введите ID пользователя для поиска:")
        # Устанавливаем состояние
    
    await callback.answer()


async def change_user_role(callback: CallbackQuery, state: FSMContext, user_repo: UserRepository):
    """Изменение роли пользователя"""
    user_id = int(callback.data.split(":")[2])
    
    # Получаем пользователя
    user = await user_repo.get_user(user_id)
    
    if not user:
        await callback.message.answer("Пользователь не найден")
        return
    
    await state.set_state(UserManagement.editing_role)
    await state.update_data(user_id=user_id)
    
    # Клавиатура выбора роли
    from tgbot.keyboards.inline import InlineKeyboardBuilder, InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    roles = ["admin", "partner", "manager", "courier", "customer"]
    for role in roles:
        builder.row(InlineKeyboardButton(
            text=f"📌 {role.capitalize()}",
            callback_data=f"set_role:{role}"
        ))
    
    await callback.message.answer(
        f"Выберите новую роль для {user['full_name']}:",
        reply_markup=builder.as_markup()
    )