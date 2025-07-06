"""
Simplified Playwright tests for frontend JavaScript functionality.
This test detects JavaScript errors in the browser and verifies Alpine.js integration.
"""

import pytest

# Import Playwright with helpful error message
try:
    from playwright.sync_api import sync_playwright
except ImportError as e:
    pytest.skip(
        "Playwright is not installed or Chromium browser is missing.\n"
        "Please run the following commands:\n"
        "  uv pip install -r requirements-dev.txt\n"
        "  playwright install chromium\n"
        "  playwright install-deps  # Install system dependencies\n"
        f"Original error: {e}",
        allow_module_level=True    )


def test_frontend_javascript_errors():
    """Test that the frontend loads without critical JavaScript errors"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            # Capture JavaScript errors and all console errors
            js_errors = []
            console_errors = []

            page.on("pageerror", lambda error: js_errors.append(str(error)))
            page.on(
                "console",
                lambda msg: console_errors.append({
                    "type": msg.type,
                    "text": msg.text,
                    "location": msg.location
                })
            )
            # save the messages to temp_msg.txt
            page.on("console", lambda msg: print(f"Console message: {msg.type} - {msg.text}"))

            # Navigate to the app
            page.goto("http://localhost:8000", timeout=10000)
            page.wait_for_load_state("networkidle", timeout=10000)

            # Check for critical errors
            alpine_errors = [
                err for err in console_errors
                if err["type"] == "error" and "Alpine Expression Error" in err["text"]
            ]
            reference_errors = [
                err for err in console_errors
                if err["type"] == "error" and "ReferenceError" in err["text"] and "not defined" in err["text"]
            ]

            # Check for textarea presence
            textarea_present = page.query_selector("#messageInput") is not None
            if not textarea_present:
                console_errors.append({
                    "type": "error",
                    "text": "Error: <textarea id='messageInput'> not found in the DOM",
                    "location": {}
                })
                pytest.fail("Critical error: <textarea id='messageInput'> not found in the DOM")
                
                
            # check for any uncaught referenceerror. 
            uncaught_reference_errors = [
                err for err in console_errors
                if err["type"] == "error" and "Uncaught ReferenceError" in err["text"]
            ]
            if uncaught_reference_errors:
                reference_errors.extend(uncaught_reference_errors)
            # add this to the report
            if reference_errors:
                print("\n🚨 Uncaught Reference Errors:")
                for error in reference_errors[:3]:
                    print(f"   - {error['text']} (at {error['location']})")
                    

            # Report findings
            print("\n📊 Frontend JavaScript Error Analysis:")
            print(f"   JavaScript Errors: {len(js_errors)}")
            print(f"   Alpine Expression Errors: {len(alpine_errors)}")
            print(f"   Reference Errors: {len(reference_errors)}")
            print(f"   Total Console Errors: {len(console_errors)}")

            if alpine_errors:
                print("\n🚨 Sample Alpine Expression Errors:")
                for error in alpine_errors[:3]:
                    print(f"   - {error['text']}")

            if reference_errors:
                print("\n🚨 Sample Reference Errors:")
                for error in reference_errors[:3]:
                    print(f"   - {error['text']}")

            # Print all console errors for debugging
            if console_errors:
                print("\n📝 All Console Errors:")
                for err in console_errors:
                    if err["type"] == "error":
                        print(f"   - {err['text']} (at {err['location']})")

            # Test should fail if there are critical errors
            total_critical_errors = len(alpine_errors) + len(reference_errors)
            if total_critical_errors > 0:
                pytest.fail(
                    f"Frontend has {total_critical_errors} critical JavaScript errors. "
                    "Alpine.js components are not loading properly."
                )

            print("\n✅ Frontend JavaScript validation passed - no critical errors detected")

            context.close()
            browser.close()

    except Exception as e:
        if "Host system is missing dependencies" in str(e):
            pytest.skip(
                f"Playwright system dependencies missing: {e}. "
                "Run 'playwright install-deps' to install them."
            )
        else:
            pytest.fail(f"Playwright test failed: {e}")


def test_alpine_components_accessible():
    """Test that Alpine.js components are accessible and defined"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            
            page.goto("http://localhost:8000", timeout=10000)
            page.wait_for_load_state("networkidle", timeout=10000)
            
            # Check if Alpine.js is loaded
            alpine_loaded = page.evaluate("() => typeof Alpine !== 'undefined'")
            
            if not alpine_loaded:
                pytest.fail("Alpine.js is not loaded on the page")
            
            # Check for Alpine data elements
            alpine_elements = page.query_selector_all("[x-data]")
            print(f"\n📊 Alpine.js Elements Found: {len(alpine_elements)}")
            
            # Check specific components referenced in HTML
            components_in_html = [
                "connectionStatus",
                "toolsDropdown", 
                "dataSourcesDropdown",
                "llmDropdown",
                "chatApp",
                "toastManager"
            ]
            
            missing_components = []
            for component in components_in_html:
                elements = page.query_selector_all(f"[x-data*='{component}']")
                if len(elements) == 0:
                    missing_components.append(component)
                    
            if missing_components:
                print(f"\n⚠️  Missing Alpine.js components in HTML: {missing_components}")
            else:
                print("\n✅ All expected Alpine.js components found in HTML")
            
            context.close()
            browser.close()
            
    except Exception as e:
        if "Host system is missing dependencies" in str(e):
            pytest.skip(f"Playwright system dependencies missing: {e}. Run 'playwright install-deps' to install them.")
        else:
            pytest.fail(f"Playwright test failed: {e}")


def test_static_file_loading():
    """Test that static files load without 404 errors"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            
            # Track failed requests
            failed_requests = []
            page.on("requestfailed", lambda request: failed_requests.append(request.url))
            
            page.goto("http://localhost:8000", timeout=10000)
            page.wait_for_load_state("networkidle", timeout=10000)
            
            # Filter for JS/CSS failures (ignore favicon)
            js_css_failures = [url for url in failed_requests 
                              if url.endswith(('.js', '.css')) and 'favicon' not in url]
            
            print(f"\n📊 Static File Loading:")
            print(f"   Total Failed Requests: {len(failed_requests)}")
            print(f"   JS/CSS Failed Requests: {len(js_css_failures)}")
            
            if js_css_failures:
                print(f"\n🚨 Failed Static Files:")
                for url in js_css_failures:
                    print(f"   - {url}")
                pytest.fail(f"Static file loading failures detected: {js_css_failures}")
            
            print("\n✅ All static files loaded successfully")
            
            context.close()
            browser.close()
            
    except Exception as e:
        if "Host system is missing dependencies" in str(e):
            pytest.skip(f"Playwright system dependencies missing: {e}. Run 'playwright install-deps' to install them.")
        else:
            pytest.fail(f"Playwright test failed: {e}")

from playwright.sync_api import sync_playwright

def test_page_load_fails_on_any_error():
    """
    Loads a page and fails if any unhandled exceptions OR
    console error messages are detected.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # A single list to hold all captured errors
        all_errors = []

        # 1. Listen for unhandled exceptions (for script-crashing errors)
        def handle_page_error(error):
            all_errors.append(f"UNHANDLED EXCEPTION: {str(error)}")
        
        page.on("pageerror", handle_page_error)

        # 2. Listen for console messages (for framework-handled errors like Alpine's)
        def handle_console_message(msg):
            # Check if the message type is 'error'
            if msg.type == 'error':
                all_errors.append(f"CONSOLE ERROR: {msg.text}")
        
        page.on("console", handle_console_message)

        try:
            # Navigate to your application
            page.goto("http://localhost:8000", timeout=10000, wait_until="networkidle")

            # An additional short wait can sometimes help catch async errors
            page.wait_for_timeout(1000)

        except Exception as e:
            # Fail the test immediately if navigation itself fails
            assert False, f"Test setup failed: Could not navigate or wait for idle. {e}"

        finally:
            # Assert that the combined list of errors is empty.
            # If not, the test will fail and print all captured errors.
            if all_errors:
                # Use '\n- ' to format each error on a new line for readability
                error_messages = "\n- ".join(all_errors)
                assert not all_errors, f"JavaScript errors found on page:\n- {error_messages}"

            browser.close()
from playwright.sync_api import sync_playwright

def test_debug_and_discover_console_output():
    """
    DEBUGGING TEST: This test's only purpose is to capture and print
    ALL console messages to the terminal to see how an error is being logged.
    """
    with sync_playwright() as p:
        # IMPORTANT: Run in headful mode to visually compare the browser and terminal
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("\n--- Starting Console Capture ---")

        # Capture ALL console messages without filtering.
        # Print them immediately to the terminal.
        def log_all_console_messages(msg):
            print(f"PLAYWRIGHT CAPTURED [{msg.type.upper()}]: {msg.text}")
        
        page.on("console", log_all_console_messages)
        
        # Also log any unhandled exceptions, just in case
        page.on("pageerror", lambda err: print(f"PLAYWRIGHT CAPTURED [PAGEERROR]: {err}"))

        try:
            page.goto("http://localhost:8000", timeout=15000)
            
            # Wait longer to ensure all async operations have time to complete.
            time_out = 5 
            print("\n--- Page loaded. Waiting" +f" {time_out} seconds for async errors... ---")
            page.wait_for_timeout(time_out * 1000)

        finally:
            print("\n--- Test Finished. Closing browser. ---")
            # wait 30 seocnds to give me time to look at the browser. 
            page.wait_for_timeout(30000)
            browser.close()


if __name__ == "__main__":
    # Allow running this test directly
    test_frontend_javascript_errors()
    test_alpine_components_accessible()
    test_static_file_loading()
    test_simple_page_load_console()
    print("\n🎉 All frontend tests completed!")