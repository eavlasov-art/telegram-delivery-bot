import asyncpg
from typing import Optional

from tgbot.config import DatabaseConfig


async def create_db_pool(config: DatabaseConfig) -> asyncpg.Pool:
    """Создание пула соединений с БД"""
    return await asyncpg.create_pool(
        host=config.host,
        port=config.port,
        user=config.user,
        password=config.password,
        database=config.database,
        min_size=config.min_size,
        max_size=config.max_size,
        command_timeout=config.command_timeout,
        max_queries=50000,
        max_inactive_connection_lifetime=300,
    )


class Repository:
    """Базовый класс для работы с БД"""
    
    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn
    
    async def fetch(self, query: str, *args):
        """Выполнение запроса с возвратом результатов"""
        return await self.conn.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args):
        """Выполнение запроса с возвратом одной строки"""
        return await self.conn.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args):
        """Выполнение запроса с возвратом одного значения"""
        return await self.conn.fetchval(query, *args)
    
    async def execute(self, query: str, *args):
        """Выполнение запроса без возврата результатов"""
        return await self.conn.execute(query, *args)
    
    async def transaction(self):
        """Создание транзакции"""
        return self.conn.transaction()


class UserRepository(Repository):
    """Работа с пользователями"""
    
    async def get_user(self, user_id: int):
        return await self.fetchrow(
            "SELECT * FROM users WHERE user_id = $1",
            user_id
        )
    
    async def create_user(self, user_id: int, username: str, full_name: str, role: str = "customer"):
        return await self.fetchrow(
            """
            INSERT INTO users (user_id, username, full_name, role, created_at)
            VALUES ($1, $2, $3, $4, NOW())
            ON CONFLICT (user_id) DO UPDATE
            SET username = EXCLUDED.username,
                full_name = EXCLUDED.full_name
            RETURNING *
            """,
            user_id, username, full_name, role
        )
    
    async def update_role(self, user_id: int, role: str):
        return await self.execute(
            "UPDATE users SET role = $1 WHERE user_id = $2",
            role, user_id
        )


class OrderRepository(Repository):
    """Работа с заказами"""
    
    async def create_order(self, customer_id: int, **data):
        # Логика создания заказа
        pass
    
    async def get_order(self, order_id: int):
        # Получение заказа
        pass
    
    async def assign_courier(self, order_id: int, courier_id: int):
        # Назначение курьера
        pass