from aiogram_dialog import setup_dialogs
from aiogram import Router

# Здесь будут импорты твоих диалогов, например:
# from .shop_dialog import shop_dialog

def register_dialogs(router: Router):
    """
    В версии aiogram_dialog 2.0+ больше нет DialogRegistry.
    Теперь мы просто подключаем диалоги как роутеры.
    """
    # router.include_router(shop_dialog) # Пример подключения
    
    # Инициализация поддержки диалогов для всего роутера/диспетчера
    setup_dialogs(router)