from aiogram import Dispatcher, F
from aiogram.enums import ChatType
from aiogram.filters import Command

from tgbot.filters.role import AdminFilter
from tgbot.handlers.groups.set_city_group import set_orders_group, set_couriers_group, set_events_group


def register_group(dp: Dispatcher):
    dp.message.register(set_orders_group, Command("set_orders_group"),
                        F.chat_type.in_([ChatType.SUPERGROUP, ChatType.GROUP]), AdminFilter())
    dp.message.register(set_couriers_group, Command("set_couriers_group"),
                        F.chat_type.in_([ChatType.SUPERGROUP, ChatType.GROUP]), AdminFilter())
    dp.message.register(set_events_group, Command("set_events_group"),
                        F.chat_type.in_([ChatType.SUPERGROUP, ChatType.GROUP]), AdminFilter())
