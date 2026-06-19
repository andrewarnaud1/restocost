"""Pytest configuration and fixtures."""

from collections.abc import AsyncGenerator, Generator
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app


@pytest.fixture
def client() -> Generator[TestClient]:
    """Provide FastAPI test client.

    Yields:
        TestClient: The FastAPI test client instance.
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def mock_db_session() -> AsyncGenerator[AsyncMock]:
    """Provide mock async database session.

    Yields:
        AsyncMock: Mock database session for testing.
    """
    mock_session = AsyncMock(spec=AsyncSession)
    yield mock_session


@pytest.fixture
def mock_db_healthy() -> Generator[Any]:
    """Mock check_db_connection to return True (healthy database).

    Yields:
        Mock: The mock patch object.
    """
    with patch("app.routers.health.check_db_connection", return_value=True):
        yield


@pytest.fixture
def mock_db_unhealthy() -> Generator[Any]:
    """Mock check_db_connection to return False (unhealthy database).

    Yields:
        Mock: The mock patch object.
    """
    with patch("app.routers.health.check_db_connection", return_value=False):
        yield
