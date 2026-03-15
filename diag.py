# diagnostic.py
import os
from dotenv import load_dotenv

print("1. Загружаем .env файл")
load_dotenv()

print("2. Читаем переменные:")
admin_ids_env = os.getenv('ADMIN_IDS')
print(f"   RAW ADMIN_IDS: '{admin_ids_env}'")
print(f"   Тип: {type(admin_ids_env)}")

if admin_ids_env:
    print(f"   Длина: {len(admin_ids_env)}")
    print(f"   ASCII коды: {[ord(c) for c in admin_ids_env]}")

print("\n3. Пробуем распарсить:")
try:
    ids = [int(id_.strip()) for id_ in admin_ids_env.split(",") if id_.strip()]
    print(f"   Успешно: {ids}")
except Exception as e:
    print(f"   Ошибка: {e}")

print("\n4. Все переменные окружения:")
for key, value in os.environ.items():
    if 'BOT' in key or 'ADMIN' in key or 'DB_' in key:
        print(f"   {key}: {value}")