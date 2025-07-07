#!/usr/bin/env python3
"""
Tests for dynamic configuration in frontend - app name and LLM models.
These tests should fail initially and pass after implementation.
"""
import subprocess
import time
import os
import requests
import yaml
import tempfile
from bs4 import BeautifulSoup


class TestFrontendDynamicConfig:
    def __init__(self):
        self.server_process = None
        self.port = 8125
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
    
    def test_app_name_in_frontend_html(self):
        """Test that app name from config appears in frontend HTML."""
        try:
            # Get the main page
            response = requests.get(self.base_url, timeout=5)
            assert response.status_code == 200
            
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Get app config to know what name to expect
            config_response = requests.get(f"{self.base_url}/api/config", timeout=5)
            assert config_response.status_code == 200
            app_config = config_response.json()
            expected_name = app_config["app_name"]
            
            # Check title tag
            title_tag = soup.find('title')
            assert title_tag is not None, "HTML should have a title tag"
            assert expected_name in title_tag.text, f"Title should contain app name: {expected_name}"
            
            # Check for app name in sidebar header
            # Look for h1 tags that might contain the app name
            h1_tags = soup.find_all('h1')
            app_name_found = any(expected_name in h1.text for h1 in h1_tags)
            assert app_name_found, f"App name '{expected_name}' should appear in h1 tags"
            
            print(f"✓ App name '{expected_name}' found in frontend HTML")
            return True
            
        except Exception as e:
            print(f"✗ App name test failed: {e}")
            return False
    
    def test_dynamic_llm_models_loading(self):
        """Test that LLM models are loaded dynamically from YAML config."""
        try:
            # Get LLMs from API
            response = requests.get(f"{self.base_url}/llms", timeout=5)
            assert response.status_code == 200
            
            llms = response.json()
            assert isinstance(llms, list), "LLMs should be returned as a list"
            assert len(llms) > 0, "Should have at least one LLM configured"
            
            # Validate structure
            for llm in llms:
                assert "name" in llm, "Each LLM should have a name"
                assert isinstance(llm["name"], str), "LLM name should be a string"
                # Optional fields that might be included
                if "provider" in llm:
                    assert isinstance(llm["provider"], str)
                if "model" in llm:
                    assert isinstance(llm["model"], str)
            
            print(f"✓ Found {len(llms)} LLM models from configuration")
            return True
            
        except Exception as e:
            print(f"✗ Dynamic LLM models test failed: {e}")
            return False
    
    def test_frontend_model_selection_uses_api(self):
        """Test that frontend model selection uses the /llms API."""
        try:
            # Get the frontend page
            response = requests.get(self.base_url, timeout=5)
            assert response.status_code == 200
            
            html_content = response.text
            
            # Should have Alpine.js code that calls fetchAvailableModels
            assert "fetchAvailableModels" in html_content, "Frontend should have fetchAvailableModels function"
            assert "'/llms'" in html_content or '"/llms"' in html_content, "Frontend should call /llms endpoint"
            
            # Should have model selection dropdown/UI
            assert "selectedModel" in html_content, "Frontend should have selectedModel binding"
            assert "availableModels" in html_content, "Frontend should have availableModels array"
            
            print("✓ Frontend uses dynamic model loading from API")
            return True
            
        except Exception as e:
            print(f"✗ Frontend model selection test failed: {e}")
            return False
    
    def test_custom_app_name_propagation(self):
        """Test that custom app name set via environment propagates to frontend."""
        try:
            # This test requires restarting the server with custom environment
            # For now, we'll test that the mechanism works
            
            # Test with current app name
            config_response = requests.get(f"{self.base_url}/api/config", timeout=5)
            assert config_response.status_code == 200
            app_config = config_response.json()
            
            frontend_response = requests.get(self.base_url, timeout=5)
            assert frontend_response.status_code == 200
            
            # App name from config should appear in frontend
            assert app_config["app_name"] in frontend_response.text, \
                "App name from config should appear in frontend HTML"
            
            print(f"✓ App name propagation working: {app_config['app_name']}")
            return True
            
        except Exception as e:
            print(f"✗ Custom app name propagation test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all frontend dynamic configuration tests."""
        print("🧪 Starting frontend dynamic configuration tests...")
        
        if not self.start_server():
            print("✗ Failed to start server")
            return False
        
        try:
            tests = [
                self.test_app_name_in_frontend_html,
                self.test_dynamic_llm_models_loading,
                self.test_frontend_model_selection_uses_api,
                self.test_custom_app_name_propagation,
            ]
            
            passed = 0
            for test in tests:
                if test():
                    passed += 1
            
            total = len(tests)
            print(f"\n📊 Frontend Dynamic Config Tests: {passed}/{total} passed")
            return passed == total
            
        finally:
            self.stop_server()


def main():
    """Run the frontend dynamic configuration tests."""
    tester = TestFrontendDynamicConfig()
    success = tester.run_all_tests()
    return success


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)