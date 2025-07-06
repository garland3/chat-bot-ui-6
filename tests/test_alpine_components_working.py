import pytest
import requests
from playwright.sync_api import sync_playwright, Page, expect, TimeoutError

def test_alpine_components_work_after_fix(page: Page):
    """
    This test should pass after the HTML fix, confirming Alpine components work.
    """
    
    # Quick server check - exit early if server isn't running
    try:
        response = requests.get("http://localhost:8000/", timeout=2)
        if response.status_code != 200:
            pytest.skip("Server not responding properly")
    except requests.RequestException:
        pytest.skip("Server not running on localhost:8000")
    
    # A list to capture ALL console messages for debugging
    console_messages = []
    page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))

    try:
        page.goto("http://localhost:8000", timeout=5000)
        
        # Wait for the page to load
        page.wait_for_load_state("networkidle", timeout=3000)
        
        # Look for the connection status text that should appear
        # Use a more specific selector
        status_element = page.locator('.status-text')
        
        # Wait for the status text to contain either "Connected" or "Disconnected"
        # This should happen quickly if Alpine components are working
        expect(status_element).to_contain_text("Connected", timeout=3000)
        
        print("✓ Alpine components are working correctly!")
        
    except Exception as e:
        # Show all console messages for debugging
        all_messages = "\n- ".join(console_messages) if console_messages else "No console messages captured"
        console_errors = [msg for msg in console_messages if msg.startswith('error:')]
        
        pytest.fail(
            f"Test failed: {str(e)}\n"
            f"All Console Messages:\n- {all_messages}\n\n"
            f"Console Errors: {len(console_errors)}"
        )