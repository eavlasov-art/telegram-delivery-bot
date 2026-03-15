from aiogram import Dispatcher
from aiogram_dialog import DialogRegistry

from .broadcast import broadcast_dialog


def register_dialogs(dp: Dispatcher):
    """Регистрация всех диалогов"""
    registry = DialogRegistry(dp)
    registry.register(broadcast_dialog)