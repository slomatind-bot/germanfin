"""Доменный слой: SQLAlchemy модель LogEntry.

Изолирована от инфраструктуры — не знает про engine, сессии, FastAPI.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class LogEntry(Base):
    """Запись лога в системе.

    Поля:
        id        — первичный ключ (автоинкремент)
        source    — откуда пришёл лог (имя сервиса, модуля)
        message   — текст сообщения
        level     — уровень: info / warn / error
        timestamp — когда запись создана (UTC)
    """

    __tablename__ = "log_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    level: Mapped[str] = mapped_column(String(10), nullable=False, default="info")
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<LogEntry id={self.id} level={self.level} source={self.source}>"
