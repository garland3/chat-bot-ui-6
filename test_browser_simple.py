#!/usr/bin/env python3
"""
Simple browser testing using subprocess instead of Playwright.
Much more reliable and faster.
"""
import subprocess
import threading
import time
import os
import signal
import sys
import requests
from urllib.parse import urljoin

class SimpleBrowserTest:
    def __init__(self):
        self.server_process = None
        self.port = 8123
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
            "--log-level", "error",
            "--reload"
        ]
        
        self.server_process = subprocess.Popen(
            cmd, 
            env=env,
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        
        # Wait for server to be ready
        for _ in range(30):  # 3 seconds max
            try:
                response = requests.get(f"{self.base_url}/health", timeout=1)
                if response.status_code == 200:
                    print(f"✓ Server started on {self.base_url}")
                    return True
            except:
                time.sleep(0.1)
        
        print("✗ Server failed to start")
        return False
    
    def stop_server(self):
        """Stop the server."""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait(timeout=5)
    
    def test_frontend_loads(self):
        """Test that frontend HTML loads correctly."""
        try:
            response = requests.get(self.base_url, timeout=5)
            assert response.status_code == 200
            content = response.text
            
            # Check for key elements
            assert "Chat Bot UI 6" in content
            assert 'x-data="chatApp()"' in content
            assert 'x-model="selectedModel"' in content
            assert 'x-model="selectedTools"' in content
            assert 'x-model="selectedDataSources"' in content
            
            # Check for modern ChatGPT-style UI elements
            assert 'type="checkbox"' in content
            assert 'Loading models...' in content
            assert 'Loading tools...' in content
            assert 'w-80 bg-gray-50' in content  # Sidebar
            assert 'h-screen flex' in content  # Full screen layout
            assert 'rounded-2xl' in content  # Chat bubbles
            assert 'Start a conversation' in content  # Empty state
            
            print("✓ Frontend loads with correct Alpine.js components")
            return True
        except Exception as e:
            print(f"✗ Frontend load test failed: {e}")
            return False
    
    def test_api_endpoints(self):
        """Test key API endpoints."""
        tests = [
            ("/health", "Health check"),
            ("/llms", "LLM configs"),
        ]
        
        for endpoint, description in tests:
            try:
                response = requests.get(urljoin(self.base_url, endpoint), timeout=5)
                if response.status_code != 200:
                    print(f"✗ {description} endpoint failed: HTTP {response.status_code}")
                    print(f"  Response: {response.text[:200]}")
                    return False
                print(f"✓ {description} endpoint works")
            except Exception as e:
                print(f"✗ {description} endpoint failed: {e}")
                return False
        
        return True
    
    def test_chat_session_creation(self):
        """Test chat session creation."""
        try:
            response = requests.post(
                urljoin(self.base_url, "/chat"),
                json={},
                timeout=5
            )
            if response.status_code != 200:
                print(f"✗ Chat session creation failed: HTTP {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                return False
            data = response.json()
            if "session_id" not in data:
                print(f"✗ Chat session creation failed: no session_id in response")
                return False
            print("✓ Chat session creation works")
            return True
        except Exception as e:
            print(f"✗ Chat session creation failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests."""
        print("🚀 Starting simple browser tests...")
        
        if not self.start_server():
            return False
        
        try:
            tests = [
                self.test_frontend_loads,
                self.test_api_endpoints, 
                self.test_chat_session_creation,
            ]
            
            passed = 0
            for test in tests:
                if test():
                    passed += 1
            
            total = len(tests)
            print(f"\n📊 Results: {passed}/{total} tests passed")
            return passed == total
            
        finally:
            self.stop_server()

def main():
    """Run the tests."""
    tester = SimpleBrowserTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()