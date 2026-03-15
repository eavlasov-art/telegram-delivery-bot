import asyncio
import asyncpg
from tgbot.config import settings

async def create_tables():
    """Создание таблиц в базе данных"""
    conn = await asyncpg.connect(
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME,
        host=settings.DB_HOST,
        port=settings.DB_PORT
    )
    
    # Читаем SQL скрипт
    with open('create_tables.sql', 'r') as f:
        sql = f.read()
    
    # Выполняем скрипт
    await conn.execute(sql)
    await conn.close()
    print("Таблицы успешно созданы!")

if __name__ == "__main__":
    asyncio.run(create_tables())