from aiogram import Dispatcher
from .role import RoleFilter, AdminFilter, IsPartner, IsManager, IsCourier, IsCustomer
from .chat_type import ChatTypeFilter


def register_all_filters(dp: Dispatcher):
    """Регистрация всех фильтров"""
    dp.message.filter(RoleFilter())
    dp.callback_query.filter(RoleFilter())
    dp.message.filter(ChatTypeFilter(chat_type=["private"]))