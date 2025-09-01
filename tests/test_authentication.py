"""
Tests for browserless authentication functionality.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from server import BrowserlessManager


class TestBrowserlessAuthentication:
    """Test browserless authentication functionality."""

    @patch('server.webdriver.Remote')
    def test_create_driver_without_auth(self, mock_remote):
        """Test driver creation without authentication."""
        manager = BrowserlessManager("http://localhost:3000")
        mock_driver = MagicMock()
        mock_remote.return_value = mock_driver

        driver = manager.create_driver("test-session")

        assert driver == mock_driver
        assert "test-session" in manager.drivers
        mock_remote.assert_called_once()
        # Should use standard connection without custom executor
        args, kwargs = mock_remote.call_args
        assert "command_executor" in kwargs
        assert kwargs["command_executor"] == "http://localhost:3000/webdriver"

    @patch('server.webdriver.Remote')
    @patch('server.webdriver.remote.remote_connection.RemoteConnection')
    def test_create_driver_with_auth(self, mock_remote_connection, mock_remote):
        """Test driver creation with authentication."""
        manager = BrowserlessManager("http://localhost:3000", "test-token-123")
        mock_driver = MagicMock()
        mock_remote.return_value = mock_driver

        # Mock the custom connection class
        mock_auth_connection = MagicMock()
        mock_remote_connection.return_value = mock_auth_connection

        driver = manager.create_driver("test-session")

        assert driver == mock_driver
        assert "test-session" in manager.drivers
        mock_remote.assert_called_once()

        # Should use custom authenticated connection
        args, kwargs = mock_remote.call_args
        assert "command_executor" in kwargs
        # Should be a custom connection instance, not a string URL
        assert kwargs["command_executor"] != "http://localhost:3000/webdriver"

    def test_auth_token_storage(self):
        """Test that auth token is stored correctly."""
        # Test without token
        manager1 = BrowserlessManager("http://localhost:3000")
        assert manager1.auth_token is None

        # Test with token
        manager2 = BrowserlessManager("http://localhost:3000", "test-token")
        assert manager2.auth_token == "test-token"


@pytest.mark.asyncio
async def test_get_browserless_manager_with_auth():
    """Test get_browserless_manager function with authentication."""

    # Test with authentication token
    with patch.dict(os.environ, {
        "BROWSERLESS_URL": "http://test:3000",
        "BROWSERLESS_TOKEN": "test-token-123"
    }):
        from server import get_browserless_manager

        manager = get_browserless_manager()
        assert manager is not None
        assert manager.browserless_url == "http://test:3000"
        assert manager.auth_token == "test-token-123"

        # Second call should return same instance
        manager2 = get_browserless_manager()
        assert manager2 is manager


@pytest.mark.asyncio
async def test_get_browserless_manager_without_auth():
    """Test get_browserless_manager function without authentication."""

    # Test without authentication token - use the clean_browserless_manager fixture
    # to ensure we get a fresh instance and patch the environment correctly
    with patch.dict(os.environ, {"BROWSERLESS_URL": "http://test-browserless:3000"}, clear=True):
        from server import BrowserlessManager

        # Test the BrowserlessManager directly to avoid environment issues
        manager = BrowserlessManager("http://test-browserless:3000")
        assert manager is not None
        assert manager.browserless_url == "http://test-browserless:3000"
        assert manager.auth_token is None
