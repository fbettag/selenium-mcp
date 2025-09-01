"""Pytest configuration for Selenium MCP tests."""

import os
from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def mock_browserless_url():
    """Automatically mock BROWSERLESS_URL for all tests."""
    with patch.dict(os.environ, {"BROWSERLESS_URL": "http://test-browserless:3000"}):
        yield


@pytest.fixture
def mock_browserless_token():
    """Mock BROWSERLESS_TOKEN when needed."""
    with patch.dict(os.environ, {"BROWSERLESS_TOKEN": "test-token"}):
        yield


@pytest.fixture
def clean_browserless_manager():
    """Ensure browserless_manager is reset between tests."""
    import server
    original = server.browserless_manager
    server.browserless_manager = None
    yield
    server.browserless_manager = original
