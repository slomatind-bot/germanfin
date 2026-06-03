"""Слой инфраструктуры базы данных.

Содержит engine, фабрику сессий и зависимость FastAPI.
Вышележащие слои (use cases / controllers) не знают про SQLAlchemy —
они получают готовую сессию через get_db.
"""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

# --- Engine ---
engine = create_engine(
    settings.DB_URL,
    connect_args=settings.DB_CONNECT_ARGS,
    echo=False,  # Не плодить шум в логах
)

# --- Фабрика сессий ---
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    """Базовый класс для всех SQLAlchemy моделей."""
    pass


def init_db() -> None:
    """Создать таблицы при первом запуске."""
    import app.models  # noqa: F401 — регистрируем модели в Base.metadata
    Base.metadata.create_all(bind=engine)


def get_db() -> AsyncGenerator[Session, None]:
    """FastAPI-зависимость: выдаёт сессию БД и закрывает после запроса."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbSession = Annotated[Session, Depends(get_db)]
