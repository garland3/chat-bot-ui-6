#!/usr/bin/env python3
"""
Debug script to test Playwright browser launching in container environment
"""
import asyncio
import os
import sys
from playwright.async_api import async_playwright


async def test_browser_launch():
    """Test basic browser launch"""
    print("Starting Playwright browser launch test...")
    print(f"Environment: {os.environ.get('DISPLAY', 'No DISPLAY set')}")
    print(f"Running as user: {os.getuid()}")
    
    try:
        async with async_playwright() as p:
            print("Playwright instance created successfully")
            
            # Try launching browser with specific options for containers
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-software-rasterizer',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-features=TranslateUI',
                    '--disable-ipc-flooding-protection',
                    '--disable-extensions',
                    '--force-device-scale-factor=1',
                    '--hide-scrollbars',
                    '--mute-audio',
                    '--no-first-run',
                    '--no-default-browser-check',
                    '--no-pings',
                    '--window-size=1280,720'
                ]
            )
            print("Browser launched successfully")
            
            context = await browser.new_context()
            print("Browser context created")
            
            page = await context.new_page()
            print("Page created")
            
            # Test navigation
            await page.goto("http://localhost:8000/health", timeout=5000)
            print("Navigation completed")
            
            title = await page.title()
            print(f"Page title: {title}")
            
            await browser.close()
            print("Browser closed successfully")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    result = asyncio.run(test_browser_launch())
    print(f"Test result: {'SUCCESS' if result else 'FAILED'}")
    sys.exit(0 if result else 1)
