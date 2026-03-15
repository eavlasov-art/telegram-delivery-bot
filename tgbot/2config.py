from enum import Enum
from pathlib import Path
from typing import Optional, List, Union

from pydantic import PostgresDsn, RedisDsn, field_validator
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotMode(str, Enum):
    """Режимы работы бота"""
    POLLING = "polling"
    WEBHOOK = "webhook"


class LogLevel(str, Enum):
    """Уровни логирования"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class DatabaseConfig(BaseModel):
    """Конфигурация PostgreSQL"""
    host: str = Field(..., description="Хост базы данных")
    port: int = Field(5432, description="Порт базы данных")
    user: str = Field(..., description="Пользователь базы данных")
    password: str = Field(..., description="Пароль базы данных")
    database: str = Field(..., description="Имя базы данных")
    min_size: int = Field(10, description="Минимальный размер пула соединений")
    max_size: int = Field(20, description="Максимальный размер пула соединений")
    command_timeout: int = Field(60, description="Таймаут выполнения команд")
    
    @property
    def dsn(self) -> str:
        """Формирование DSN строки"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    @property
    def asyncpg_dsn(self) -> str:
        """Формирование DSN строки для asyncpg"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class RedisConfig(BaseModel):
    """Конфигурация Redis"""
    host: str = Field("localhost", description="Хост Redis")
    port: int = Field(6379, description="Порт Redis")
    password: Optional[str] = Field(None, description="Пароль Redis")
    db: int = Field(0, description="Номер базы данных Redis")
    use_redis: bool = Field(False, description="Использовать ли Redis для FSM")
    
    @property
    def dsn(self) -> str:
        """Формирование DSN строки"""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"


class BotConfig(BaseModel):
    """Конфигурация Telegram бота"""
    token: str = Field(..., description="Токен бота из @BotFather", min_length=45, max_length=50)
    admin_ids: List[int] = Field(default_factory=list, description="Список ID администраторов")
    mode: BotMode = Field(BotMode.POLLING, description="Режим работы бота")
    skip_updates: bool = Field(True, description="Пропускать накопившиеся обновления при запуске")
    
    @field_validator('token')
    @classmethod
    def validate_token(cls, v: str) -> str:
        """Валидация формата токена"""
        if not v.replace(':', '').isalnum():
            raise ValueError('Токен должен содержать только буквы, цифры и двоеточие')
        return v


class WebhookConfig(BaseModel):
    """Конфигурация вебхуков (если используется режим webhook)"""
    domain: Optional[str] = Field(None, description="Домен для вебхука")
    path: str = Field("/webhook", description="Путь для вебхука")
    host: str = Field("0.0.0.0", description="Хост для веб-сервера")
    port: int = Field(8080, description="Порт для веб-сервера")
    max_connections: int = Field(40, description="Максимальное количество соединений")
    
    @property
    def url(self) -> Optional[str]:
        """Полный URL вебхука"""
        if self.domain:
            return f"https://{self.domain}{self.path}"
        return None


class LoggingConfig(BaseModel):
    """Конфигурация логирования"""
    level: LogLevel = Field(LogLevel.INFO, description="Уровень логирования")
    format: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Формат логов"
    )
    date_format: str = Field("%Y-%m-%d %H:%M:%S", description="Формат даты")
    log_chat_id: Optional[int] = Field(None, description="Chat ID для отправки логов")
    enable_file_logging: bool = Field(False, description="Логировать ли в файл")
    log_file: Path = Field(Path("logs/bot.log"), description="Путь к файлу логов")


class SchedulerConfig(BaseModel):
    """Конфигурация планировщика задач"""
    enabled: bool = Field(False, description="Включить планировщик")
    timezone: str = Field("Europe/Moscow", description="Часовой пояс")
    job_defaults: dict = Field(
        default_factory=lambda: {
            'coalesce': False,
            'max_instances': 3,
            'misfire_grace_time': 3600
        },
        description="Настройки задач по умолчанию"
    )


class Settings(BaseSettings):
    """Главный класс конфигурации"""
    
    # Режим работы
    BOT_MODE: BotMode = BotMode.POLLING
    SKIP_UPDATES: bool = True
    
    # Telegram Bot
    BOT_TOKEN: str
    ADMIN_IDS: str = ""  # ДОЛЖНО БЫТЬ СТРОКОЙ, НЕ СПИСКОМ!
    
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
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    @field_validator('ADMIN_IDS', mode='before')
    @classmethod
    def parse_admin_ids(cls, v: str) -> List[int]:
        """Парсинг списка администраторов из строки"""
        print(f"=== ОТЛАДКА parse_admin_ids ===")
        print(f"Входное значение v: {v}")
        print(f"Тип v: {type(v)}")
        
        # Если v - уже список, логируем это как проблему
        if isinstance(v, list):
            print(f"⚠️ ВНИМАНИЕ: Получен список вместо строки: {v}")
            # Принудительно преобразуем обратно в строку
            v = ",".join(str(x) for x in v)
            print(f"Преобразовано в строку: {v}")
        
        if not v:
            return []
        
        try:
            # Разделяем по запятой и убираем пробелы
            ids = []
            for part in v.split(","):
                part = part.strip()
                if part:  # Пропускаем пустые части
                    ids.append(int(part))
            print(f"Результат парсинга: {ids}")
            return ids
        except ValueError as e:
            print(f"ОШИБКА парсинга: {e}")
            raise ValueError(f"ADMIN_IDS должен содержать числа, разделенные запятыми: {e}")
    
    @property
    def bot(self) -> BotConfig:
        """Получение конфигурации бота"""
        return BotConfig(
            token=self.BOT_TOKEN,
            admin_ids=self.ADMIN_IDS,  # Здесь уже список!
            mode=self.BOT_MODE,
            skip_updates=self.SKIP_UPDATES
        )    
    @property
    def db(self) -> DatabaseConfig:
        """Получение конфигурации базы данных"""
        return DatabaseConfig(
            host=self.DB_HOST,
            port=self.DB_PORT,
            user=self.DB_USER,
            password=self.DB_PASSWORD,
            database=self.DB_NAME,
            min_size=self.DB_MIN_SIZE,
            max_size=self.DB_MAX_SIZE,
            command_timeout=self.DB_COMMAND_TIMEOUT
        )
    
    @property
    def redis(self) -> RedisConfig:
        """Получение конфигурации Redis"""
        return RedisConfig(
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            password=self.REDIS_PASSWORD,
            db=self.REDIS_DB,
            use_redis=self.USE_REDIS
        )
    
    @property
    def webhook(self) -> WebhookConfig:
        """Получение конфигурации вебхуков"""
        return WebhookConfig(
            domain=self.WEBHOOK_DOMAIN,
            path=self.WEBHOOK_PATH,
            host=self.WEBHOOK_HOST,
            port=self.WEBHOOK_PORT,
            max_connections=self.WEBHOOK_MAX_CONNECTIONS
        )
    
    @property
    def logging(self) -> LoggingConfig:
        """Получение конфигурации логирования"""
        return LoggingConfig(
            level=self.LOG_LEVEL,
            log_chat_id=self.LOG_CHAT_ID,
            enable_file_logging=self.ENABLE_FILE_LOGGING,
            log_file=Path(self.LOG_FILE) if self.LOG_FILE else None
        )
    
    @property
    def scheduler(self) -> SchedulerConfig:
        """Получение конфигурации планировщика"""
        return SchedulerConfig(
            enabled=self.SCHEDULER_ENABLED,
            timezone=self.SCHEDULER_TIMEZONE
        )
    
    def setup_logging(self):
        """Настройка логирования на основе конфигурации"""
        import logging
        from logging.handlers import RotatingFileHandler
        
        # Базовые настройки
        logging.basicConfig(
            level=self.logging.level.value,
            format=self.logging.format,
            datefmt=self.logging.date_format
        )
        
        # Логирование в файл если нужно
        if self.logging.enable_file_logging:
            log_path = self.BASE_DIR / self.logging.log_file
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = RotatingFileHandler(
                log_path,
                maxBytes=10*1024*1024,  # 10 MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setFormatter(logging.Formatter(
                self.logging.format,
                self.logging.date_format
            ))
            logging.getLogger().addHandler(file_handler)


# Создание глобального экземпляра конфигурации
settings = Settings()

# Функция для перезагрузки конфигурации (полезно при горячей перезагрузке)
def reload_settings():
    """Перезагрузка конфигурации из .env файла"""
    global settings
    settings = Settings()


# Функция для быстрого получения конфига
def get_settings() -> Settings:
    """Получение текущих настроек"""
    return settings


# Пример .env файла (можно сохранить как .env.example)
ENV_EXAMPLE = """
# Telegram Bot Configuration
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_IDS=12345678,87654321,11223344
BOT_MODE=polling  # или webhook
SKIP_UPDATES=true

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=strong_password
DB_NAME=delivery_bot
DB_MIN_SIZE=10
DB_MAX_SIZE=20

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=optional_password
REDIS_DB=0
USE_REDIS=false

# Webhook Configuration (only if BOT_MODE=webhook)
WEBHOOK_DOMAIN=your-domain.com
WEBHOOK_PATH=/webhook
WEBHOOK_PORT=8080

# Logging Configuration
LOG_LEVEL=INFO
LOG_CHAT_ID=-1001234567890
ENABLE_FILE_LOGGING=false
LOG_FILE=logs/bot.log

# Scheduler Configuration
SCHEDULER_ENABLED=true
SCHEDULER_TIMEZONE=Europe/Moscow
"""