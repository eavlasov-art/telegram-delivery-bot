from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from tgbot.services.database import OrderRepository


async def cmd_orders(message: Message):
    """Команда /orders"""
    await message.answer(
        "📋 <b>Ваши заказы</b>\n\n"
        "Функционал в разработке"
    )


async def new_order(message: Message, state: FSMContext):
    """Начать создание нового заказа"""
    await message.answer(
        "📦 <b>Создание нового заказа</b>\n\n"
        "Функционал в разработке"
    )


async def my_orders(message: Message, order_repo: OrderRepository):
    """Показать список заказов пользователя"""
    # Временно возвращаем заглушку
    await message.answer(
        "📋 <b>Ваши заказы</b>\n\n"
        "У вас пока нет заказов"
    )


async def order_details(callback: CallbackQuery):
    """Показать детали заказа"""
    await callback.answer("Детали заказа в разработке")
    await callback.message.edit_text(
        "📝 <b>Детали заказа</b>\n\n"
        "Функционал в разработке"
    )


async def cancel_order(callback: CallbackQuery):
    """Отменить заказ"""
    await callback.answer("Заказ отменен")
    await callback.message.edit_text(
        "❌ Заказ отменен"
    )