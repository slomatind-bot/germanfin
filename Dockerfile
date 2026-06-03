# ============================================================
# Stage 1: Builder — устанавливаем зависимости
# ============================================================
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# ============================================================
# Stage 2: Runtime — минимальный образ
# ============================================================
FROM python:3.11-slim AS runtime

# Создаём не-root пользователя
RUN adduser --disabled-password --gecos "" appuser

WORKDIR /app

# Копируем весь установленный site-packages из builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Копируем исходный код
COPY app/ ./app/
COPY tests/ ./tests/

# Директория для SQLite БД
RUN mkdir -p /app/data /app/app && chown -R appuser:appuser /app /app/app /app/data

# Переключаемся на не-root
USER appuser

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/health').read())"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
