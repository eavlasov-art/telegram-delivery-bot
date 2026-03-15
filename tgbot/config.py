from enum import Enum
from pathlib import Path
from typing import Optional, List, Any

from pydantic import field_validator, BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# --- Вспомогательные перечисления ---
class BotMode(str, Enum):
    POLLING = "polling"
    WEBHOOK = "webhook"

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

# --- Подмодели конфигурации ---
class DatabaseConfig(BaseModel):
    host: str
    port: int
    user: str
    password: str
    database: str
    min_size: int = 10
    max_size: int = 20
    command_timeout: int = 60
    
    @property
    def dsn(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

class RedisConfig(BaseModel):
    host: str
    port: int
    password: Optional[str] = None
    db: int = 0
    use_redis: bool = False

class BotConfig(BaseModel):
    token: str
    admin_ids: List[int]
    mode: BotMode
    skip_updates: bool

# --- ГЛАВНЫЙ КЛАСС НАСТРОЕК ---
class Settings(BaseSettings):
    # Telegram Bot
    BOT_TOKEN: str
    BOT_MODE: BotMode = BotMode.POLLING
    SKIP_UPDATES: bool = True
    # Указываем Union, чтобы валидатор мог принять строку и вернуть список
    ADMIN_IDS: List[int] = Field(default_factory=list)

    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_MIN_SIZE: int = 10
    DB_MAX_SIZE: int = 20
    DB_COMMAND_TIMEOUT: int = 60

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    USE_REDIS: bool = False

    # Webhook
    WEBHOOK_DOMAIN: Optional[str] = None
    WEBHOOK_PATH: str = "/webhook"
    WEBHOOK_HOST: str = "0.0.0.0"
    WEBHOOK_PORT: int = 8080

    # Logging
    LOG_LEVEL: LogLevel = LogLevel.INFO
    LOG_FILE: str = "logs/bot.log"
    ENABLE_FILE_LOGGING: bool = False
    LOG_CHAT_ID: Optional[int] = None

    # Scheduler
    SCHEDULER_ENABLED: bool = False
    SCHEDULER_TIMEZONE: str = "Europe/Moscow"

    # Настройки Pydantic
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False, # Лучше False для Windows/Linux совместимости
        extra="ignore"
    )

    @field_validator('ADMIN_IDS', mode='before')
    @classmethod
    def parse_admin_ids(cls, v: Any) -> List[int]:
        """Исправленный парсинг ID админов"""
        if isinstance(v, str) and v.strip():
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        if isinstance(v, int):
            return [v]
        if isinstance(v, list):
            return [int(x) for x in v]
        return []

    # --- Properties для удобного доступа ---
    @property
    def bot(self) -> BotConfig:
        return BotConfig(
            token=self.BOT_TOKEN,
            admin_ids=self.ADMIN_IDS,
            mode=self.BOT_MODE,
            skip_updates=self.SKIP_UPDATES
        )

    @property
    def db(self) -> DatabaseConfig:
        return DatabaseConfig(
            host=self.DB_HOST, port=self.DB_PORT, user=self.DB_USER,
            password=self.DB_PASSWORD, database=self.DB_NAME,
            min_size=self.DB_MIN_SIZE, max_size=self.DB_MAX_SIZE,
            command_timeout=self.DB_COMMAND_TIMEOUT
        )

# Инициализация
try:
    settings = Settings()
except Exception as e:
    print(f"❌ Ошибка в конфигурации: {e}")
    raise

def get_settings() -> Settings:
    return settings