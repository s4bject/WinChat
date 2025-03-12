import pytest
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def db_session():
    """Мок асинхронной сессии базы данных"""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture(scope="session")
def anyio_backend():
    """Настройка pytest-asyncio"""
    return "asyncio"
