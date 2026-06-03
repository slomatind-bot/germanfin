"""Точка входа FastAPI-приложения.

Собирает все компоненты вместе: lifespan (инициализация БД),
регистрирует роуты и middleware.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from app.core.database import init_db
from app.routers import analysis, logs
from app.schemas import HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Жизненный цикл приложения.

    startup:
        — создаёт таблицы в БД, если их нет
    shutdown:
        — (в будущем) закрытие соединений, если понадобится
    """
    init_db()
    yield


app = FastAPI(
    title="FastAPI Logger",
    description="Простой API-сервер для сбора и просмотра логов",
    version="0.1.0",
    lifespan=lifespan,
)

# --- Роуты ---
app.include_router(logs.router)
app.include_router(analysis.router)


# --- Healthcheck ---
@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["system"],
    summary="Проверка работоспособности",
)
def health() -> HealthResponse:
    """Вернуть OK, если приложение живо."""
    return HealthResponse(status="ok")


# --- Глобальный обработчик 500 ---
@app.exception_handler(Exception)
def global_exception_handler(request, exc: Exception) -> JSONResponse:
    """Поймать необработанные ошибки и вернуть 500."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "type": type(exc).__name__},
    )
