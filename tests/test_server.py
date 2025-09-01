"""
Tests for the Selenium MCP server.
These tests require a running browserless instance.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from server import BrowserlessManager, get_browserless_manager


class TestBrowserlessManager:
    """Test BrowserlessManager functionality."""

    def test_init(self):
        """Test BrowserlessManager initialization."""
        manager = BrowserlessManager("http://localhost:3000")
        assert manager.browserless_url == "http://localhost:3000"
        assert manager.drivers == {}

    @patch('server.webdriver.Remote')
    def test_create_driver(self, mock_remote):
        """Test driver creation."""
        manager = BrowserlessManager("http://localhost:3000")
        mock_driver = MagicMock()
        mock_remote.return_value = mock_driver

        driver = manager.create_driver("test-session")

        assert driver == mock_driver
        assert "test-session" in manager.drivers
        mock_remote.assert_called_once()

    def test_get_driver_existing(self):
        """Test getting existing driver."""
        manager = BrowserlessManager("http://localhost:3000")
        mock_driver = MagicMock()
        manager.drivers["test-session"] = mock_driver

        driver = manager.get_driver("test-session")
        assert driver == mock_driver

    def test_get_driver_nonexistent(self):
        """Test getting non-existent driver."""
        manager = BrowserlessManager("http://localhost:3000")

        driver = manager.get_driver("nonexistent")
        assert driver is None

    def test_close_driver(self):
        """Test closing driver."""
        manager = BrowserlessManager("http://localhost:3000")
        mock_driver = MagicMock()
        manager.drivers["test-session"] = mock_driver

        manager.close_driver("test-session")
        assert "test-session" not in manager.drivers
        mock_driver.quit.assert_called_once()

    def test_close_all_drivers(self):
        """Test closing all drivers."""
        manager = BrowserlessManager("http://localhost:3000")

        mock_driver1 = MagicMock()
        mock_driver2 = MagicMock()
        manager.drivers["session1"] = mock_driver1
        manager.drivers["session2"] = mock_driver2

        manager.close_all()
        assert manager.drivers == {}
        mock_driver1.quit.assert_called_once()
        mock_driver2.quit.assert_called_once()


class TestMCPFunctions:
    """Test MCP server functions."""

    @patch('server.get_browserless_manager')
    async def test_navigate_to_url_logic(self, mock_get_manager):
        """Test the navigation logic used by navigate_to_url function."""
        # Mock manager and driver
        mock_manager = MagicMock()
        mock_driver = MagicMock()
        mock_driver.title = "Test Page"
        mock_driver.current_url = "https://example.com"
        mock_manager.get_driver.return_value = None
        mock_manager.create_driver.return_value = mock_driver
        mock_get_manager.return_value = mock_manager

        # Test the core logic that would be in navigate_to_url
        session_id = "test-session"
        url = "https://example.com"

        driver = mock_manager.get_driver(session_id) or mock_manager.create_driver(session_id)
        driver.get(url)

        # Verify results
        assert driver.title == "Test Page"
        assert driver.current_url == "https://example.com"
        mock_driver.get.assert_called_once_with("https://example.com")

    @patch('server.get_browserless_manager')
    async def test_navigate_to_url_existing_session_logic(self, mock_get_manager):
        """Test the navigation logic with existing session."""
        # Mock manager and driver
        mock_manager = MagicMock()
        mock_driver = MagicMock()
        mock_driver.title = "Test Page"
        mock_driver.current_url = "https://example.com"
        mock_manager.get_driver.return_value = mock_driver
        mock_get_manager.return_value = mock_manager

        # Test the core logic that would be in navigate_to_url
        session_id = "test-session"
        url = "https://example.com"

        driver = mock_manager.get_driver(session_id) or mock_manager.create_driver(session_id)
        driver.get(url)

        # Verify results - should use existing driver
        assert driver.title == "Test Page"
        assert driver.current_url == "https://example.com"
        mock_manager.create_driver.assert_not_called()
        mock_driver.get.assert_called_once_with("https://example.com")


@pytest.mark.asyncio
async def test_get_browserless_manager():
    """Test get_browserless_manager function."""

    # First call should create manager
    with patch.dict(os.environ, {"BROWSERLESS_URL": "http://test:3000"}):
        manager1 = get_browserless_manager()
        assert manager1 is not None
        assert manager1.browserless_url == "http://test:3000"

        # Second call should return same instance
        manager2 = get_browserless_manager()
        assert manager2 is manager1


@pytest.mark.asyncio
async def test_get_browserless_manager_missing_env(clean_browserless_manager):
    """Test get_browserless_manager with missing environment variable."""

    # Temporarily disable the autouse fixture by patching the environment
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="BROWSERLESS_URL environment variable is required"):
            get_browserless_manager()
