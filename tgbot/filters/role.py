from typing import Union, List

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery


class RoleFilter(BaseFilter):
    """Фильтр для проверки роли пользователя"""
    
    def __init__(self, roles: Union[str, List[str]] = None, allow_admin: bool = True):
        self.roles = [roles] if isinstance(roles, str) else roles
        self.allow_admin = allow_admin
    
    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        # Получаем роль из данных (устанавливается в RoleMiddleware)
        role = getattr(event, "role", None)
        
        if not role:
            # Если роль не установлена, пробуем получить из event.data
            if hasattr(event, "from_user"):
                user_id = event.from_user.id
                # Здесь можно добавить загрузку роли из БД если нет middleware
                return False
        
        # Администраторы имеют доступ ко всему
        if self.allow_admin and role == "admin":
            return True
        
        # Если список ролей не указан, пропускаем всех (кроме unknown)
        if not self.roles:
            return role != "unknown"
        
        # Проверяем соответствие роли
        return role in self.roles


class AdminFilter(BaseFilter):
    """Фильтр только для администраторов"""
    
    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        role = getattr(event, "role", None)
        return role == "admin"


class IsPartner(BaseFilter):
    """Фильтр для партнеров"""
    
    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        role = getattr(event, "role", None)
        return role == "partner"


class IsManager(BaseFilter):
    """Фильтр для менеджеров"""
    
    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        role = getattr(event, "role", None)
        return role == "manager"


class IsCourier(BaseFilter):
    """Фильтр для курьеров"""
    
    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        role = getattr(event, "role", None)
        return role == "courier"


class IsCustomer(BaseFilter):
    """Фильтр для заказчиков"""
    
    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        role = getattr(event, "role", None)
        return role == "customer"