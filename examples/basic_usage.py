#!/usr/bin/env python3
"""
Basic usage example for the Selenium MCP Server.
This demonstrates how to interact with the MCP server programmatically.
"""

import asyncio
import json

import httpx


async def test_selenium_mcp():
    """Test the Selenium MCP server functionality."""

    # MCP server URL (assuming it's running locally)
    mcp_url = "http://localhost:8000"

    async with httpx.AsyncClient() as client:

        print("Testing Selenium MCP Server...")

        # Test 1: Navigate to a URL
        print("\n1. Navigating to example.com...")
        navigate_payload = {
            "arguments": {
                "url": "https://example.com"
            }
        }

        response = await client.post(
            f"{mcp_url}/call/navigate_to_url",
            json=navigate_payload,
            timeout=30.0
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✓ Navigation successful: {result['content']}")
        else:
            print(f"✗ Navigation failed: {response.text}")
            return

        # Test 2: Get page info
        print("\n2. Getting page information...")
        page_info_payload = {
            "arguments": {}
        }

        response = await client.post(
            f"{mcp_url}/call/get_page_info",
            json=page_info_payload,
            timeout=10.0
        )

        if response.status_code == 200:
            result = response.json()
            page_info = json.loads(result['content'])
            print(f"✓ Page title: {page_info.get('title', 'Unknown')}")
            print(f"✓ Page URL: {page_info.get('url', 'Unknown')}")
        else:
            print(f"✗ Page info failed: {response.text}")

        # Test 3: Find an element
        print("\n3. Finding h1 element...")
        find_element_payload = {
            "arguments": {
                "selector": "h1",
                "by": "tag_name"
            }
        }

        response = await client.post(
            f"{mcp_url}/call/find_element",
            json=find_element_payload,
            timeout=10.0
        )

        if response.status_code == 200:
            result = response.json()
            element_info = json.loads(result['content'])
            print(f"✓ Found element: {element_info.get('tag_name', 'Unknown')}")
            print(f"✓ Element text: {element_info.get('text', 'No text')}")
        else:
            print(f"✗ Find element failed: {response.text}")

        # Test 4: Execute JavaScript
        print("\n4. Executing JavaScript...")
        js_payload = {
            "arguments": {
                "script": "return document.title;"
            }
        }

        response = await client.post(
            f"{mcp_url}/call/execute_javascript",
            json=js_payload,
            timeout=10.0
        )

        if response.status_code == 200:
            result = response.json()
            js_result = json.loads(result['content'])
            print(f"✓ JavaScript executed: {js_result.get('result', 'No result')}")
        else:
            print(f"✗ JavaScript execution failed: {response.text}")

        # Test 5: Close browser
        print("\n5. Closing browser session...")
        close_payload = {
            "arguments": {}
        }

        response = await client.post(
            f"{mcp_url}/call/close_browser",
            json=close_payload,
            timeout=10.0
        )

        if response.status_code == 200:
            result = response.json()
            close_result = json.loads(result['content'])
            print(f"✓ {close_result.get('message', 'Browser closed')}")
        else:
            print(f"✗ Close browser failed: {response.text}")

        print("\n✅ All tests completed!")


if __name__ == "__main__":
    asyncio.run(test_selenium_mcp())
