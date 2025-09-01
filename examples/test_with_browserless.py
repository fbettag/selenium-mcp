#!/usr/bin/env python3
"""
Test script that demonstrates using the Selenium MCP server with a local browserless instance.
This script assumes you have browserless running locally on port 3000.
"""

import asyncio
import os
import subprocess
import time

import httpx


async def start_browserless():
    """Start browserless in a Docker container."""
    print("Starting browserless container...")

    try:
        # Check if browserless is already running
        async with httpx.AsyncClient() as client:
            await client.get("http://localhost:3000/health", timeout=2.0)
            print("✓ Browserless is already running")
            return None
    except Exception:
        pass

    # Start browserless container
    cmd = [
        "docker", "run", "--rm", "-d",
        "-p", "3000:3000",
        "-e", "CONNECTION_TIMEOUT=30000",
        "-e", "MAX_CONCURRENT_SESSIONS=5",
        "--name", "selenium-test-browserless",
        "browserless/chrome:latest"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Browserless container started")

            # Wait for browserless to be ready
            print("Waiting for browserless to be ready...")
            for _ in range(30):  # 30 second timeout
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.get("http://localhost:3000/health", timeout=1.0)
                        if response.status_code == 200:
                            print("✓ Browserless is ready")
                            return "selenium-test-browserless"
                except Exception:
                    pass
                time.sleep(1)

            print("✗ Browserless failed to start within timeout")
            return None
        else:
            print(f"✗ Failed to start browserless: {result.stderr}")
            return None
    except Exception as e:
        print(f"✗ Error starting browserless: {e}")
        return None


async def stop_browserless(container_name):
    """Stop the browserless container."""
    if container_name:
        print(f"Stopping browserless container {container_name}...")
        try:
            subprocess.run(["docker", "stop", container_name], capture_output=True)
            print("✓ Browserless container stopped")
        except Exception as e:
            print(f"✗ Error stopping browserless: {e}")


async def test_mcp_server():
    """Test the MCP server with browserless."""

    # Start browserless
    container_name = await start_browserless()
    if not container_name:
        print("Skipping MCP server test due to browserless issues")
        return

    try:
        # Set environment variable for MCP server
        os.environ["BROWSERLESS_URL"] = "http://localhost:3000"

        # Import and test the MCP server
        from selenium.webdriver.common.by import By

        from server import get_browserless_manager

        print("\nTesting MCP server functionality...")

        # Test basic navigation
        manager = get_browserless_manager()

        # Create a test session
        session_id = "test-session-123"

        try:
            # Test 1: Create driver and navigate
            print("1. Creating browser session and navigating...")
            driver = manager.create_driver(session_id)
            driver.get("https://httpbin.org/html")

            # Test 2: Get page title
            title = driver.title
            print(f"✓ Page title: {title}")

            # Test 3: Find elements
            print("2. Finding elements...")
            h1_element = driver.find_element(By.TAG_NAME, "h1")
            print(f"✓ Found h1: {h1_element.text}")

            # Test 4: Execute JavaScript
            print("3. Executing JavaScript...")
            js_result = driver.execute_script("return document.title;")
            print(f"✓ JavaScript result: {js_result}")

            # Test 5: Take screenshot
            print("4. Taking screenshot...")
            screenshot = driver.get_screenshot_as_base64()
            print(f"✓ Screenshot taken ({len(screenshot)} bytes)")

            print("\n✅ All MCP server tests passed!")

        except Exception as e:
            print(f"✗ Test failed: {e}")

        finally:
            # Clean up
            manager.close_driver(session_id)

    except Exception as e:
        print(f"✗ MCP server test failed: {e}")

    finally:
        # Stop browserless
        await stop_browserless(container_name)


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
