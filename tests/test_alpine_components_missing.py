import pytest
import requests
from playwright.sync_api import sync_playwright, Page, expect, TimeoutError

def test_page_fails_if_alpine_components_are_missing(page: Page):
    """
    This test correctly fails because the Alpine components are loaded after Alpine.js
    initializes, so the status text is never set and console errors occur.
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
        page.goto("http://localhost:8000", timeout=3000)

        # The key to a failing test:
        # Wait for a specific outcome that will NEVER happen if the component is broken.
        # We expect the text to be 'Connected' or 'Disconnected'.
        # The selector `text=/Connected|Disconnected/` uses a regular expression.
        page.wait_for_selector('text=/Connected|Disconnected/', timeout=2000)

    except TimeoutError:
        # Filter for actual errors
        console_errors = [msg for msg in console_messages if msg.startswith('error:')]
        
        # Show all console messages for debugging
        all_messages = "\n- ".join(console_messages) if console_messages else "No console messages captured"
        
        pytest.fail(
            "Test failed as expected. The page timed out waiting for an Alpine component to render.\n"
            f"All Console Messages:\n- {all_messages}\n\n"
            f"Console Errors: {len(console_errors)}"
        )

    # If the test somehow passes the wait (e.g., if the HTML is fixed),
    # this final check ensures it still fails if there were any background errors.
    console_errors = [msg for msg in console_messages if msg.startswith('error:')]
    if console_errors:
        error_list = "\n- ".join(console_errors)
        pytest.fail(f"Unexpected JS errors were found on the page:\n- {error_list}")