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

class LoggingConfig(BaseModel):
    level: LogLevel = LogLevel.INFO
    format: str = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    log_file: str = "logs/bot.log"
    enable_file_logging: bool = False
    log_chat_id: Optional[int] = None

class SchedulerConfig(BaseModel):
    enabled: bool = False
    timezone: str = "Europe/Moscow"

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

    @property
    def redis(self) -> RedisConfig:
        return RedisConfig(
            host=self.REDIS_HOST, port=self.REDIS_PORT, password=self.REDIS_PASSWORD,
            db=self.REDIS_DB, use_redis=self.USE_REDIS
        )

    @property
    def logging(self) -> LoggingConfig:
        return LoggingConfig(
            level=self.LOG_LEVEL,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            log_file=self.LOG_FILE,
            enable_file_logging=self.ENABLE_FILE_LOGGING,
            log_chat_id=self.LOG_CHAT_ID
        )

    @property
    def webhook(self) -> dict:
        return {
            "url": self.WEBHOOK_DOMAIN + self.WEBHOOK_PATH if self.WEBHOOK_DOMAIN else None,
            "path": self.WEBHOOK_PATH,
            "host": self.WEBHOOK_HOST,
            "port": self.WEBHOOK_PORT,
            "max_connections": 100
        }

    @property
    def scheduler(self) -> SchedulerConfig:
        return SchedulerConfig(
            enabled=self.SCHEDULER_ENABLED,
            timezone=self.SCHEDULER_TIMEZONE
        )

# Инициализация
try:
    settings = Settings()
except Exception as e:
    print(f"❌ Ошибка в конфигурации: {e}")
    raise

def get_settings() -> Settings:
    return settings