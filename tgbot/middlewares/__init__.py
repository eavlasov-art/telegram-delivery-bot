from .db import DbMiddleware
from .role import RoleMiddleware
from .throttling import ThrottlingMiddleware
from .logging import LoggingMiddleware
from .support import SupportMiddleware


def register_all_middlewares(dp, pool):
    """Регистрация всех мидлварей"""
    dp.message.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware())
    
    dp.update.middleware(DbMiddleware(pool))
    dp.update.middleware(LoggingMiddleware())
    dp.update.middleware(RoleMiddleware())
    dp.update.middleware(SupportMiddleware())