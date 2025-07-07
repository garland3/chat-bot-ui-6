#!/usr/bin/env python3
"""
Unit tests for frontend message rendering to prevent regressions.
"""
import subprocess
import time
import os
import requests
from bs4 import BeautifulSoup
import re


class TestMessageRendering:
    def __init__(self):
        self.server_process = None
        self.port = 8124
        self.base_url = f"http://localhost:{self.port}"
        
    def start_server(self):
        """Start the FastAPI server in background."""
        env = os.environ.copy()
        env.update({
            "DISABLE_LLM_CALLS": "true",
            "TEST_MODE": "true", 
            "TEST_EMAIL": "test@example.com"
        })
        
        cmd = [
            "uv", "run", "uvicorn", 
            "app.main:app", 
            "--host", "127.0.0.1", 
            "--port", str(self.port),
            "--log-level", "error"
        ]
        
        self.server_process = subprocess.Popen(
            cmd, 
            env=env,
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        
        # Wait for server to be ready
        for _ in range(30):
            try:
                response = requests.get(f"{self.base_url}/health", timeout=1)
                if response.status_code == 200:
                    return True
            except:
                time.sleep(0.1)
        
        return False
    
    def stop_server(self):
        """Stop the server."""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait(timeout=5)
    
    def test_message_rendering_consistency(self):
        """Test that user and assistant messages use consistent text rendering."""
        try:
            response = requests.get(self.base_url, timeout=5)
            assert response.status_code == 200
            content = response.text
            
            # Parse HTML to check message rendering
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find user message template
            user_messages = soup.find_all('div', {'x-show': lambda x: x and 'message.role === \'user\'' in x})
            assistant_messages = soup.find_all('div', {'x-show': lambda x: x and 'message.role === \'assistant\'' in x})
            
            assert len(user_messages) > 0, "User message template not found"
            assert len(assistant_messages) > 0, "Assistant message template not found"
            
            # Check that user messages use x-text
            user_content_divs = user_messages[0].find_all('div', class_='whitespace-pre-wrap')
            assert len(user_content_divs) > 0, "User message content div not found"
            
            user_content_div = user_content_divs[0]
            assert 'x-text' in user_content_div.attrs, "User message should use x-text attribute"
            assert user_content_div.attrs.get('x-text') == 'message.content', "User message x-text should reference message.content"
            
            # Check that assistant messages also use x-text (not x-html)
            assistant_content_divs = assistant_messages[0].find_all('div', class_='whitespace-pre-wrap')
            assert len(assistant_content_divs) > 0, "Assistant message content div not found"
            
            assistant_content_div = assistant_content_divs[0]
            assert 'x-text' in assistant_content_div.attrs, "Assistant message should use x-text attribute"
            assert assistant_content_div.attrs.get('x-text') == 'message.content', "Assistant message x-text should reference message.content"
            
            # Ensure assistant messages don't use x-html (the bug we fixed)
            assert 'x-html' not in assistant_content_div.attrs, "Assistant message should NOT use x-html attribute"
            
            print("✓ Message rendering consistency test passed")
            return True
            
        except Exception as e:
            print(f"✗ Message rendering consistency test failed: {e}")
            return False
    
    def test_alpine_message_structure(self):
        """Test that Alpine.js message structure is correct."""
        try:
            response = requests.get(self.base_url, timeout=5)
            assert response.status_code == 200
            content = response.text
            
            # Check for proper Alpine.js message loop
            assert 'x-for="message in messages"' in content, "Message loop template not found"
            assert ':key="message.id"' in content, "Message key binding not found"
            
            # Check for all message roles
            assert 'x-show="message.role === \'user\'"' in content, "User message conditional not found"
            assert 'x-show="message.role === \'assistant\'"' in content, "Assistant message conditional not found"
            assert 'x-show="message.role === \'system\'"' in content, "System message conditional not found"
            
            # Verify all message types use x-text consistently
            text_bindings = re.findall(r'x-text="message\.content"', content)
            html_bindings = re.findall(r'x-html="message\.content"', content)
            
            # Should have exactly 3 x-text bindings (user, assistant, system)
            assert len(text_bindings) == 3, f"Expected 3 x-text bindings, found {len(text_bindings)}"
            
            # Should have no x-html bindings for message.content
            assert len(html_bindings) == 0, f"Found unexpected x-html bindings: {len(html_bindings)}"
            
            print("✓ Alpine.js message structure test passed")
            return True
            
        except Exception as e:
            print(f"✗ Alpine.js message structure test failed: {e}")
            return False
    
    def test_message_styling(self):
        """Test that message styling is consistent."""
        try:
            response = requests.get(self.base_url, timeout=5)
            assert response.status_code == 200
            content = response.text
            
            # Check for proper message bubble styling
            assert 'rounded-2xl' in content, "Chat bubble styling not found"
            assert 'whitespace-pre-wrap' in content, "Text wrapping class not found"
            assert 'max-w-2xl' in content, "Message width constraint not found"
            
            # Check for user message styling (blue background)
            assert 'bg-blue-600 text-white' in content, "User message styling not found"
            
            # Check for assistant message styling (gray background)
            assert 'bg-gray-100 dark:bg-gray-800' in content, "Assistant message styling not found"
            
            # Check for system message styling (yellow background) 
            assert 'bg-yellow-100 dark:bg-yellow-900' in content, "System message styling not found"
            
            print("✓ Message styling test passed")
            return True
            
        except Exception as e:
            print(f"✗ Message styling test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all message rendering tests."""
        print("🧪 Starting message rendering tests...")
        
        if not self.start_server():
            print("✗ Failed to start server")
            return False
        
        try:
            tests = [
                self.test_message_rendering_consistency,
                self.test_alpine_message_structure,
                self.test_message_styling,
            ]
            
            passed = 0
            for test in tests:
                if test():
                    passed += 1
            
            total = len(tests)
            print(f"\n📊 Message Rendering Tests: {passed}/{total} passed")
            return passed == total
            
        finally:
            self.stop_server()


def main():
    """Run the message rendering tests."""
    tester = TestMessageRendering()
    success = tester.run_all_tests()
    return success


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)