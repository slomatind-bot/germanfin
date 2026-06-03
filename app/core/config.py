"""Конфигурация приложения.

Слой конфигурации (infrastructure/config):
содержит все настройки, вынесенные в одно место.
В чистой архитектуре этот слой находится снаружи,
чтобы доменный слой о нём ничего не знал.
"""

from pathlib import Path


class Settings:
    """Настройки приложения.

    Все изменяемые параметры собраны здесь,
    чтобы не размазывать магические числа по коду.
    """

    # --- База данных ---
    # SQLite — файл логов в корне проекта
    DB_URL: str = "sqlite:///./logs.db"
    # Для SQLite нужно отключить проверку подключений в пуле
    DB_CONNECT_ARGS: dict = {"check_same_thread": False}

    # --- Сервер ---
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # --- Пагинация ---
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 200

    # --- Пути ---
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DB_PATH: Path = BASE_DIR / "logs.db"


# Единственный экземпляр — импортируем настройки как синглтон
settings = Settings()
