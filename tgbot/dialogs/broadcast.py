from aiogram.types import Message
from aiogram.dispatcher.router import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram_dialog import Dialog, Window, DialogRegistry
from aiogram_dialog.widgets.kbd import Button, Row, Cancel
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog import ChatEvent

from tgbot.filters.role import AdminFilter
from tgbot.services.database import UserRepository

router = Router()
dialog_router = Router()


# Состояния диалога
class BroadcastSG(StatesGroup):
    start = State()
    confirm = State()
    progress = State()
    result = State()


async def get_data(dialog_manager: DialogManager, **kwargs):
    """Получение данных для диалога"""
    return {
        "text": dialog_manager.dialog_data.get("text", ""),
        "photo": dialog_manager.dialog_data.get("photo"),
        "recipients": dialog_manager.dialog_data.get("recipients", 0)
    }


async def on_input_text(message: Message, widget, dialog_manager: DialogManager, text: str):
    """Обработка ввода текста"""
    dialog_manager.dialog_data["text"] = text
    await dialog_manager.next()


async def on_input_photo(message: Message, widget, dialog_manager: DialogManager, text: str = None):
    """Обработка получения фото"""
    if message.photo:
        dialog_manager.dialog_data["photo"] = message.photo[-1].file_id
    await dialog_manager.next()


async def on_skip_photo(callback: ChatEvent, button: Button, dialog_manager: DialogManager):
    """Пропуск добавления фото"""
    await dialog_manager.next()


async def on_confirm(callback: ChatEvent, button: Button, dialog_manager: DialogManager):
    """Подтверждение отправки"""
    await dialog_manager.switch_to(BroadcastSG.progress)
    
    # Получаем всех пользователей
    user_repo = UserRepository(dialog_manager.middleware_data["conn"])
    users = await user_repo.get_all_users()
    
    text = dialog_manager.dialog_data["text"]
    photo = dialog_manager.dialog_data.get("photo")
    
    # Счетчики
    sent = 0
    failed = 0
    
    # Отправляем сообщения
    for user in users:
        try:
            if photo:
                await dialog_manager.middleware_data["bot"].send_photo(
                    chat_id=user['user_id'],
                    photo=photo,
                    caption=text
                )
            else:
                await dialog_manager.middleware_data["bot"].send_message(
                    chat_id=user['user_id'],
                    text=text
                )
            sent += 1
        except Exception:
            failed += 1
        
        # Обновляем прогресс каждые 10 сообщений
        if (sent + failed) % 10 == 0:
            await dialog_manager.update({
                "sent": sent,
                "failed": failed,
                "total": len(users)
            })
    
    # Сохраняем результат
    dialog_manager.dialog_data.update({
        "sent": sent,
        "failed": failed,
        "total": len(users)
    })
    
    await dialog_manager.switch_to(BroadcastSG.result)


async def on_cancel(callback: ChatEvent, button: Button, dialog_manager: DialogManager):
    """Отмена рассылки"""
    await dialog_manager.done()


async def on_finish(callback: ChatEvent, button: Button, dialog_manager: DialogManager):
    """Завершение"""
    await dialog_manager.done()


# Создание диалога
broadcast_dialog = Dialog(
    # Шаг 1: Ввод текста
    Window(
        Const("📢 <b>Создание рассылки</b>\n\n"
              "Введите текст сообщения для рассылки:"),
        TextInput(
            id="text_input",
            on_success=on_input_text
        ),
        Cancel(Const("❌ Отмена")),
        state=BroadcastSG.start,
        getter=get_data
    ),
    
    # Шаг 2: Добавление фото (опционально)
    Window(
        Const("📸 Отправьте фото для рассылки или пропустите этот шаг:"),
        MessageInput(
            func=on_input_photo,
            content_types=["photo"]
        ),
        Row(
            Button(Const("⏭ Пропустить"), id="skip_photo", on_click=on_skip_photo),
            Cancel(Const("❌ Отмена"))
        ),
        state=BroadcastSG.confirm,
        getter=get_data
    ),
    
    # Шаг 3: Прогресс отправки
    Window(
        Format("⏳ <b>Отправка...</b>\n\n"
               "Отправлено: {sent}\n"
               "Ошибок: {failed}\n"
               "Всего: {total}"),
        state=BroadcastSG.progress,
        getter=get_data
    ),
    
    # Шаг 4: Результат
    Window(
        Format("✅ <b>Рассылка завершена!</b>\n\n"
               "✓ Успешно отправлено: {sent}\n"
               "✗ Ошибок доставки: {failed}\n"
               "👥 Всего получателей: {total}"),
        Button(Const("🏁 Завершить"), id="finish", on_click=on_finish),
        state=BroadcastSG.result,
        getter=get_data
    ),
)


@router.message(Command("broadcast"), AdminFilter())
async def cmd_broadcast(message: Message, dialog_manager: DialogManager):
    """Команда для запуска рассылки"""
    await dialog_manager.start(BroadcastSG.start, mode=StartMode.RESET_STACK)