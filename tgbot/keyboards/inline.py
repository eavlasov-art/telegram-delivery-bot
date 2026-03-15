from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Dict, Any, Optional


def get_order_keyboard(order_id: int, role: str, status: str = None) -> InlineKeyboardMarkup:
    """Клавиатура для управления заказом"""
    builder = InlineKeyboardBuilder()
    
    if role == "customer":
        builder.row(
            InlineKeyboardButton(
                text="📝 Детали",
                callback_data=f"order_details:{order_id}"
            )
        )
        if status in ["pending", "confirmed"]:
            builder.row(
                InlineKeyboardButton(
                    text="❌ Отменить",
                    callback_data=f"order_cancel:{order_id}"
                )
            )
    
    elif role == "courier":
        builder.row(
            InlineKeyboardButton(
                text="✅ Взять заказ",
                callback_data=f"order_take:{order_id}"
            )
        )
        builder.row(
            InlineKeyboardButton(
                text="📍 Маршрут",
                callback_data=f"order_route:{order_id}"
            )
        )
    
    elif role in ["manager", "admin"]:
        builder.row(
            InlineKeyboardButton(
                text="👥 Назначить курьера",
                callback_data=f"order_assign:{order_id}"
            )
        )
        builder.row(
            InlineKeyboardButton(
                text="📊 Статус",
                callback_data=f"order_status:{order_id}"
            ),
            InlineKeyboardButton(
                text="📝 История",
                callback_data=f"order_history:{order_id}"
            )
        )
    
    return builder.as_markup()


def get_pagination_keyboard(
    prefix: str,
    current_page: int,
    total_pages: int,
    extra_data: Dict[str, Any] = None
) -> InlineKeyboardMarkup:
    """Клавиатура для пагинации"""
    builder = InlineKeyboardBuilder()
    buttons = []
    
    if current_page > 1:
        buttons.append(
            InlineKeyboardButton(
                text="◀️",
                callback_data=f"{prefix}:prev:{current_page}"
            )
        )
    
    buttons.append(
        InlineKeyboardButton(
            text=f"{current_page}/{total_pages}",
            callback_data="ignore"
        )
    )
    
    if current_page < total_pages:
        buttons.append(
            InlineKeyboardButton(
                text="▶️",
                callback_data=f"{prefix}:next:{current_page}"
            )
        )
    
    builder.row(*buttons)
    return builder.as_markup()


def get_confirmation_keyboard(action: str, item_id: int) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения действия"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Подтвердить",
            callback_data=f"confirm:{action}:{item_id}"
        ),
        InlineKeyboardButton(
            text="❌ Отмена",
            callback_data=f"cancel:{action}:{item_id}"
        )
    )
    return builder.as_markup()


def get_admin_panel_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура админ-панели"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="👥 Пользователи", callback_data="admin:users"),
        InlineKeyboardButton(text="🏙 Города", callback_data="admin:cities")
    )
    builder.row(
        InlineKeyboardButton(text="📊 Статистика", callback_data="admin:stats"),
        InlineKeyboardButton(text="📢 Рассылка", callback_data="admin:broadcast")
    )
    builder.row(
        InlineKeyboardButton(text="⚙️ Настройки", callback_data="admin:settings"),
        InlineKeyboardButton(text="📝 Логи", callback_data="admin:logs")
    )
    return builder.as_markup()