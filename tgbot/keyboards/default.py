from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_main_keyboard(role: str) -> ReplyKeyboardMarkup:
    """Главная клавиатура в зависимости от роли"""
    builder = ReplyKeyboardBuilder()
    
    # Базовые кнопки для всех
    if role == "customer":
        builder.row(
            KeyboardButton(text="📦 Новый заказ"),
            KeyboardButton(text="📋 Мои заказы")
        )
        builder.row(
            KeyboardButton(text="👤 Профиль"),
            KeyboardButton(text="📞 Поддержка")
        )
    
    elif role == "courier":
        builder.row(
            KeyboardButton(text="🚚 Доступные заказы"),
            KeyboardButton(text="✅ Мои заказы")
        )
        builder.row(
            KeyboardButton(text="🟢 Свободен"),
            KeyboardButton(text="🔴 Занят")
        )
        builder.row(
            KeyboardButton(text="👤 Профиль"),
            KeyboardButton(text="📞 Поддержка")
        )
    
    elif role == "manager":
        builder.row(
            KeyboardButton(text="📊 Все заказы"),
            KeyboardButton(text="👥 Курьеры")
        )
        builder.row(
            KeyboardButton(text="📈 Отчеты"),
            KeyboardButton(text="⚙️ Настройки")
        )
    
    elif role == "partner":
        builder.row(
            KeyboardButton(text="🏢 Мой город"),
            KeyboardButton(text="👥 Менеджеры")
        )
        builder.row(
            KeyboardButton(text="🚚 Курьеры"),
            KeyboardButton(text="📊 Статистика")
        )
    
    elif role == "admin":
        builder.row(
            KeyboardButton(text="👥 Пользователи"),
            KeyboardButton(text="🏙 Города")
        )
        builder.row(
            KeyboardButton(text="📊 Статистика"),
            KeyboardButton(text="⚙️ Настройки бота")
        )
        builder.row(
            KeyboardButton(text="📢 Рассылка"),
            KeyboardButton(text="📝 Логи")
        )
    
    return builder.as_markup(resize_keyboard=True)


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой отмены"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="❌ Отмена"))
    return builder.as_markup(resize_keyboard=True)


def get_contact_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для запроса контакта"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="📱 Отправить контакт", request_contact=True))
    builder.add(KeyboardButton(text="❌ Отмена"))
    return builder.as_markup(resize_keyboard=True)


def get_location_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для запроса локации"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="📍 Отправить локацию", request_location=True))
    builder.add(KeyboardButton(text="❌ Отмена"))
    return builder.as_markup(resize_keyboard=True)