"""Фикстуры pytest для тестов."""
import pytest
from app.core.database import init_db


@pytest.fixture(autouse=True)
def setup_db() -> None:
    """Создать таблицы БД перед каждым тестом."""
    init_db()
