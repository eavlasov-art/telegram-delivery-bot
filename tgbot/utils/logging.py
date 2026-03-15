import logging
import sys
from pathlib import Path

from loguru import logger

from tgbot.config import settings


class InterceptHandler(logging.Handler):
    """Перехват стандартных логов и перенаправление в loguru"""
    
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
            
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
            
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging():
    """Настройка логирования"""
    
    # Удаляем стандартные обработчики
    logger.remove()
    
    # Формат логов
    log_format = settings.logging.format
    
    # Добавляем вывод в консоль
    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.logging.level.value,
        colorize=True
    )
    
    # Добавляем вывод в файл если нужно
    if settings.logging.enable_file_logging:
        log_path = Path(settings.logging.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_path,
            format=log_format,
            level=settings.logging.level.value,
            rotation="10 MB",
            retention="1 month",
            compression="zip"
        )
    
    # Перехватываем стандартные логи
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Отключаем лишние логи
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.WARNING)
    
    logger.info("Логирование настроено")