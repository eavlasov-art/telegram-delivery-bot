from aiogram import Dispatcher
from aiogram_dialog import setup_dialogs

from .broadcast import broadcast_dialog, router as broadcast_router


def register_dialogs(dp: Dispatcher):
    """Регистрация всех диалогов"""
    # Регистрируем роутер с командой /broadcast
    dp.include_router(broadcast_router)
    
    # Регистрируем сам диалог
    dp.include_router(broadcast_dialog)
    
    # Настраиваем диалоги
    setup_dialogs(dp)