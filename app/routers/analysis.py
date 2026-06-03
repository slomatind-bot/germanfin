"""Слой представления: AI-анализ error-логов.

Отправляет накопившиеся error-логи в LLM через OpenRouter,
получает рекомендации по исправлению и сохраняет их в Obsidian.
"""

import os
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter
from sqlalchemy import select

from app.core.database import DbSession
from app.models import LogEntry

router = APIRouter(prefix="/logs", tags=["analysis"])


def _call_llm(prompt: str) -> str:
    """Отправить запрос в OpenRouter (LLM) и вернуть ответ."""
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    if not api_key:
        return "Ошибка: OPENROUTER_API_KEY не настроен"

    payload = {
        "model": "deepseek/deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Ты — опытный девопс-инженер. Анализируй логи ошибок "
                    "и предлагай конкретные шаги для их исправления. "
                    "Ответ давай на русском языке, структурированно."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 2000,
    }

    try:
        resp = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": "Bearer " + api_key,
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as exc:
        return f"Ошибка при вызове LLM: {exc}"


def _save_to_obsidian(title: str, content: str) -> str:
    """Сохранить отчёт анализа в Obsidian vault или локально."""
    vault_path = "/tmp/obsidian-analysis"
    os.makedirs(vault_path, exist_ok=True)

    now = datetime.now()
    filename = f"error-analysis-{now:%Y%m%d-%H%M%S}.md"
    filepath = os.path.join(vault_path, filename)

    frontmatter = (
        "---\n"
        f'title: "{title}"\n'
        f"created: {now:%Y-%m-%d %H:%M}\n"
        "tags: [error-analysis, ai, logs]\n"
        "---\n\n"
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter)
        f.write(content)

    return filepath


@router.post("/analyze")
def analyze_errors(db: DbSession):
    """Проанализировать error-логи через LLM и сохранить отчёт.

    Берёт последние 20 error-логов, отправляет в DeepSeek через OpenRouter,
    сохраняет результат в Obsidian и возвращает пользователю.
    """
    # 1. Выбираем error-логи
    stmt = (
        select(LogEntry)
        .where(LogEntry.level == "error")
        .order_by(LogEntry.timestamp.desc())
        .limit(20)
    )
    errors = list(db.execute(stmt).scalars().all())

    if not errors:
        return {
            "status": "ok",
            "message": "Нет error-логов для анализа",
            "analysis": None,
            "saved_to": None,
        }

    # 2. Формируем промпт
    log_lines = "\n".join(
        f"[{e.timestamp}] {e.source}: {e.message}" for e in errors
    )
    prompt = (
        "Проанализируй следующие логи ошибок и предложи план исправления:\n\n"
        f"{log_lines}\n\n"
        "Для каждой ошибки укажи:\n"
        "- вероятную причину\n"
        "- конкретные шаги для исправления\n"
        "- что проверить в первую очередь"
    )

    # 3. Вызываем LLM
    analysis = _call_llm(prompt)

    # 4. Сохраняем в Obsidian
    now_utc = datetime.now(timezone.utc)
    title = f"Анализ ошибок от {now_utc:%d.%m.%Y %H:%M}"
    saved_to = _save_to_obsidian(title, analysis)

    return {
        "status": "ok",
        "analyzed_count": len(errors),
        "analysis": analysis,
        "saved_to": saved_to,
    }
