"""Слой схем (application / use cases).

Pydantic-модели для валидации входящих данных
и форматирования ответов API.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class LogCreate(BaseModel):
    """Схема создания записи лога."""

    source: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Источник лога (имя сервиса/модуля)",
        examples=["fastapi-logger", "auth-service"],
    )
    message: str = Field(
        ...,
        min_length=1,
        description="Текст сообщения",
        examples=["Server started successfully"],
    )
    level: str = Field(
        default="info",
        pattern=r"^(info|warn|error)$",
        description="Уровень: info, warn или error",
        examples=["info", "warn", "error"],
    )


class LogResponse(BaseModel):
    """Схема ответа с одной записью лога."""

    id: int
    source: str
    message: str
    level: str
    timestamp: datetime

    model_config = {"from_attributes": True}


class LogListResponse(BaseModel):
    """Схема ответа со списком логов (пагинация)."""

    total: int
    skip: int
    limit: int
    items: list[LogResponse]


class HealthResponse(BaseModel):
    """Ответ healthcheck."""

    status: str = "ok"


class DeleteResponse(BaseModel):
    """Ответ на удаление."""

    deleted: int
    message: str = "Logs deleted"
