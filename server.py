#!/usr/bin/env python3
"""
Selenium MCP Server for browserless deployments.
Connects to browserless service via WebDriver protocol over TCP.
"""

import asyncio
import os
from typing import Any, Dict, Optional

from fastmcp import Context, FastMCP
from pydantic import BaseModel, Field
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

# Initialize FastMCP server
mcp = FastMCP("selenium")


# Pydantic Models for Request/Response Validation
class NavigateParams(BaseModel):
    """Parameters for navigation."""
    url: str = Field(..., description="URL to navigate to")


class NavigateResponse(BaseModel):
    """Response from navigation."""
    title: str = Field(..., description="Page title")
    current_url: str = Field(..., description="Current URL after navigation")
    success: bool = Field(default=True, description="Navigation success status")


class ElementParams(BaseModel):
    """Parameters for element operations."""
    selector: str = Field(..., description="CSS selector, XPath, or other locator")
    by: str = Field(default="css", description="Locator strategy (css, xpath, id, name, class_name, tag_name, link_text, partial_link_text)")


class ElementInfo(BaseModel):
    """Information about a found element."""
    tag_name: str = Field(..., description="HTML tag name")
    text: str = Field(..., description="Element text content")
    attributes: Dict[str, str] = Field(default_factory=dict, description="Element attributes")
    location: Dict[str, int] = Field(..., description="Element location on page")
    size: Dict[str, int] = Field(..., description="Element size")


class ClickResponse(BaseModel):
    """Response from click operation."""
    success: bool = Field(default=True, description="Click success status")
    new_title: str = Field(..., description="Page title after click")
    new_url: str = Field(..., description="URL after click")


class ScriptParams(BaseModel):
    """Parameters for JavaScript execution."""
    script: str = Field(..., description="JavaScript code to execute")


class ScriptResponse(BaseModel):
    """Response from JavaScript execution."""
    success: bool = Field(default=True, description="Execution success status")
    result: Any = Field(..., description="Result of JavaScript execution")


class ScreenshotResponse(BaseModel):
    """Response from screenshot operation."""
    screenshot: str = Field(..., description="Base64 encoded screenshot data URL")
    success: bool = Field(default=True, description="Screenshot success status")


class PageInfo(BaseModel):
    """Information about the current page."""
    title: str = Field(..., description="Page title")
    url: str = Field(..., description="Current URL")
    page_source_length: int = Field(..., description="Length of page source")
    window_handle: str = Field(..., description="Current window handle")


class CloseResponse(BaseModel):
    """Response from closing browser."""
    success: bool = Field(default=True, description="Close success status")
    message: str = Field(..., description="Status message")


class BrowserlessManager:
    """Manages browserless connections and sessions."""

    def __init__(self, browserless_url: str, auth_token: Optional[str] = None):
        self.browserless_url = browserless_url.rstrip('/')
        self.auth_token = auth_token
        self.drivers: Dict[str, WebDriver] = {}

    def create_driver(self, session_id: str, browser: str = "chrome") -> WebDriver:
        """Create a new WebDriver instance connected to browserless."""
        options = webdriver.ChromeOptions() if browser == "chrome" else webdriver.FirefoxOptions()

        # Browserless specific options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")

        # Connect to browserless with optional authentication
        executor_url = f"{self.browserless_url}/webdriver"

        if self.auth_token:
            # Add authentication headers for browserless
            from selenium.webdriver.remote.remote_connection import RemoteConnection

            class AuthenticatedRemoteConnection(RemoteConnection):
                def __init__(self, remote_server_addr, keep_alive=True, auth_token=None):
                    super().__init__(remote_server_addr, keep_alive=keep_alive)
                    self.auth_token = auth_token

                def _get_connection_headers(self, parsed_url, keep_alive):
                    headers = super()._get_connection_headers(parsed_url, keep_alive)
                    if self.auth_token:
                        headers["Authorization"] = f"Bearer {self.auth_token}"
                    return headers

            # Create custom command executor with authentication
            driver = webdriver.Remote(
                command_executor=AuthenticatedRemoteConnection(executor_url, auth_token=self.auth_token),
                options=options
            )
        else:
            # Standard connection without authentication
            driver = webdriver.Remote(
                command_executor=executor_url,
                options=options
            )

        self.drivers[session_id] = driver
        return driver

    def get_driver(self, session_id: str) -> Optional[WebDriver]:
        """Get an existing WebDriver instance."""
        return self.drivers.get(session_id)

    def close_driver(self, session_id: str):
        """Close a WebDriver instance."""
        if session_id in self.drivers:
            try:
                self.drivers[session_id].quit()
            except Exception:
                pass
            del self.drivers[session_id]

    def close_all(self):
        """Close all WebDriver instances."""
        for session_id in list(self.drivers.keys()):
            self.close_driver(session_id)


# Global browserless manager
browserless_manager: Optional[BrowserlessManager] = None


def get_browserless_manager() -> BrowserlessManager:
    """Get or create browserless manager instance."""
    global browserless_manager
    if browserless_manager is None:
        browserless_url = os.getenv("BROWSERLESS_URL")
        if not browserless_url:
            raise ValueError("BROWSERLESS_URL environment variable is required")

        # Get optional authentication token
        auth_token = os.getenv("BROWSERLESS_TOKEN")

        browserless_manager = BrowserlessManager(browserless_url, auth_token)
    return browserless_manager


@mcp.resource("browser://{url}")
async def get_browser_content(url: str, ctx: Context) -> str:
    """
    Get content from a URL using browser automation.

    Args:
        url: The URL to navigate to

    Returns:
        HTML content of the page
    """
    manager = get_browserless_manager()
    session_id = ctx.session_id

    try:
        driver = manager.create_driver(session_id)
        driver.get(url)

        # Wait for page to load
        WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.TAG_NAME, "body"))
        )

        return driver.page_source

    except Exception as e:
        raise Exception(f"Failed to get content from {url}: {str(e)}") from e


@mcp.tool()
async def navigate_to_url(params: NavigateParams, ctx: Context) -> NavigateResponse:
    """
    Navigate to a URL and return page information.
    """
    manager = get_browserless_manager()
    session_id = ctx.session_id

    try:
        driver = manager.get_driver(session_id) or manager.create_driver(session_id)
        driver.get(params.url)

        # Wait for page to load
        WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.TAG_NAME, "body"))
        )

        return NavigateResponse(
            title=driver.title,
            current_url=driver.current_url,
            success=True
        )

    except Exception as e:
        raise Exception(f"Failed to navigate to {params.url}: {str(e)}") from e


@mcp.tool()
async def find_element(params: ElementParams, ctx: Context) -> ElementInfo:
    """
    Find an element on the current page.
    """
    manager = get_browserless_manager()
    session_id = ctx.session_id

    driver = manager.get_driver(session_id)
    if not driver:
        raise Exception("No active browser session. Please navigate to a URL first.")

    try:
        by_method = {
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "id": By.ID,
            "name": By.NAME,
            "class_name": By.CLASS_NAME,
            "tag_name": By.TAG_NAME,
            "link_text": By.LINK_TEXT,
            "partial_link_text": By.PARTIAL_LINK_TEXT
        }.get(params.by.lower(), By.CSS_SELECTOR)

        element = driver.find_element(by_method, params.selector)

        return ElementInfo(
            tag_name=element.tag_name,
            text=element.text,
            attributes={
                attr: element.get_attribute(attr)
                for attr in ["id", "class", "name", "href", "src"]
                if element.get_attribute(attr)
            },
            location=element.location,
            size=element.size
        )

    except Exception as e:
        raise Exception(f"Failed to find element with {params.by} selector '{params.selector}': {str(e)}") from e


@mcp.tool()
async def click_element(params: ElementParams, ctx: Context) -> ClickResponse:
    """
    Click on an element on the current page.
    """
    manager = get_browserless_manager()
    session_id = ctx.session_id

    driver = manager.get_driver(session_id)
    if not driver:
        raise Exception("No active browser session. Please navigate to a URL first.")

    try:
        by_method = {
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "id": By.ID,
            "name": By.NAME,
            "class_name": By.CLASS_NAME,
            "tag_name": By.TAG_NAME,
            "link_text": By.LINK_TEXT,
            "partial_link_text": By.PARTIAL_LINK_TEXT
        }.get(params.by.lower(), By.CSS_SELECTOR)

        element = driver.find_element(by_method, params.selector)
        element.click()

        # Wait for potential navigation
        WebDriverWait(driver, 5).until(
            ec.presence_of_element_located((By.TAG_NAME, "body"))
        )

        return ClickResponse(
            success=True,
            new_title=driver.title,
            new_url=driver.current_url
        )

    except Exception as e:
        raise Exception(f"Failed to click element with {params.by} selector '{params.selector}': {str(e)}") from e


@mcp.tool()
async def execute_javascript(params: ScriptParams, ctx: Context) -> ScriptResponse:
    """
    Execute JavaScript in the current page context.
    """
    manager = get_browserless_manager()
    session_id = ctx.session_id

    driver = manager.get_driver(session_id)
    if not driver:
        raise Exception("No active browser session. Please navigate to a URL first.")

    try:
        result = driver.execute_script(params.script)
        return ScriptResponse(
            success=True,
            result=result
        )

    except Exception as e:
        raise Exception(f"Failed to execute JavaScript: {str(e)}") from e


@mcp.tool()
async def take_screenshot(ctx: Context) -> ScreenshotResponse:
    """
    Take a screenshot of the current page.
    """
    manager = get_browserless_manager()
    session_id = ctx.session_id

    driver = manager.get_driver(session_id)
    if not driver:
        raise Exception("No active browser session. Please navigate to a URL first.")

    try:
        screenshot = driver.get_screenshot_as_base64()
        return ScreenshotResponse(
            screenshot=f"data:image/png;base64,{screenshot}",
            success=True
        )

    except Exception as e:
        raise Exception(f"Failed to take screenshot: {str(e)}") from e


@mcp.tool()
async def close_browser(ctx: Context) -> CloseResponse:
    """
    Close the current browser session.
    """
    manager = get_browserless_manager()
    session_id = ctx.session_id

    manager.close_driver(session_id)
    return CloseResponse(success=True, message="Browser session closed")


@mcp.tool()
async def get_page_info(ctx: Context) -> PageInfo:
    """
    Get information about the current page.
    """
    manager = get_browserless_manager()
    session_id = ctx.session_id

    driver = manager.get_driver(session_id)
    if not driver:
        raise Exception("No active browser session. Please navigate to a URL first.")

    try:
        return PageInfo(
            title=driver.title,
            url=driver.current_url,
            page_source_length=len(driver.page_source),
            window_handle=driver.current_window_handle
        )

    except Exception as e:
        raise Exception(f"Failed to get page info: {str(e)}") from e


async def main():
    """Main entry point for the MCP server."""
    # Validate environment variable
    if not os.getenv("BROWSERLESS_URL"):
        print("Error: BROWSERLESS_URL environment variable is required")
        print("Example: BROWSERLESS_URL=http://browserless:3000")
        return

    browserless_url = os.getenv("BROWSERLESS_URL")
    auth_token = os.getenv("BROWSERLESS_TOKEN")

    if auth_token:
        print(f"Starting Selenium MCP Server connecting to {browserless_url} with authentication")
    else:
        print(f"Starting Selenium MCP Server connecting to {browserless_url}")

    await mcp.run()


if __name__ == "__main__":
    asyncio.run(main())
