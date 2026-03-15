from aiogram import Bot
from aiogram.types import BotCommand


async def set_default_commands(bot: Bot):
    """Установка команд меню бота"""
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="menu", description="Показать меню"),
    ]
    await bot.set_my_commands(commands)