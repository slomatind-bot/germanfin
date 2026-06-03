"""Слой представления (presentation): HTTP-роуты для работы с логами.

Принимает HTTP-запросы, делегирует работу с данными через SQLAlchemy сессию,
возвращает Pydantic-ответы.
"""

from fastapi import APIRouter, HTTPException, Query, status

from app.core.database import DbSession
from app.core.config import settings
from app.models import LogEntry
from app.schemas import (
    DeleteResponse,
    LogCreate,
    LogListResponse,
    LogResponse,
)

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("", response_model=LogListResponse)
def list_logs(
    db: DbSession,
    skip: int = Query(0, ge=0, description="Сколько записей пропустить"),
    limit: int = Query(
        settings.DEFAULT_PAGE_SIZE,
        ge=1,
        le=settings.MAX_PAGE_SIZE,
        description="Максимум записей в ответе",
    ),
) -> LogListResponse:
    """Вернуть список логов с пагинацией."""
    total = db.query(LogEntry).count()
    items = (
        db.query(LogEntry)
        .order_by(LogEntry.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return LogListResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=[LogResponse.model_validate(e) for e in items],
    )


@router.get("/{log_id}", response_model=LogResponse)
def get_log(log_id: int, db: DbSession) -> LogResponse:
    """Вернуть одну запись лога по ID."""
    entry = db.query(LogEntry).filter(LogEntry.id == log_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Log entry with id={log_id} not found",
        )
    return LogResponse.model_validate(entry)


@router.post("", response_model=LogResponse, status_code=status.HTTP_201_CREATED)
def create_log(payload: LogCreate, db: DbSession) -> LogResponse:
    """Создать новую запись лога."""
    entry = LogEntry(
        source=payload.source,
        message=payload.message,
        level=payload.level,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return LogResponse.model_validate(entry)


@router.delete("", response_model=DeleteResponse)
def clear_logs(db: DbSession) -> DeleteResponse:
    """Удалить все записи логов."""
    deleted = db.query(LogEntry).delete()
    db.commit()
    return DeleteResponse(deleted=deleted)
