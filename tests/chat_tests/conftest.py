import pytest
import pytest_mock
from unittest.mock import MagicMock, create_autospec
from sqlalchemy.orm import Session
from src.utils.cache_config import cache


@pytest.fixture(scope="function")
def mock_db_session(mocker):
    """Fixture to mock the SQLAlchemy database session."""
    session_mock = create_autospec(Session, instance=True)
    # Additional setup for mocking session methods can be done here
    yield session_mock


@pytest.fixture(scope="function")
def mock_cache(mocker):
    """Fixture to mock the cache system."""
    cache_mock = mocker.patch("src.utils.cache_config.cache")
    # Assuming 'cache' is a simple key-value store, we simulate it with a dict
    cache_mock.get = MagicMock(side_effect=lambda key: None)
    cache_mock.set = MagicMock()
    cache_mock.delete = MagicMock()
    yield cache_mock
