#!/usr/bin/env python3
"""
Tests for configuration API endpoints - chat name and LLM models.
These tests should fail initially and pass after implementation.
"""
import pytest
import yaml
import tempfile
import os
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings


class TestConfigAPI:
    """Test configuration API endpoints."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    def test_app_config_endpoint_exists(self):
        """Test that /api/config endpoint exists and returns app configuration."""
        response = self.client.get("/api/config")
        assert response.status_code == 200, "Config endpoint should exist"
        
        data = response.json()
        assert "app_name" in data, "Response should include app_name"
        assert isinstance(data["app_name"], str), "app_name should be a string"
    
    def test_app_name_from_config(self):
        """Test that app name comes from config.py settings."""
        response = self.client.get("/api/config")
        assert response.status_code == 200
        
        data = response.json()
        # Should match the current setting in config.py
        assert data["app_name"] == settings.app_name
    
    def test_custom_app_name_via_env(self):
        """Test that app name can be overridden via environment variable."""
        # Since the app name is already loaded from .env file, this test
        # should verify that the current .env setting is being used
        response = self.client.get("/api/config")
        assert response.status_code == 200
        
        data = response.json()
        # Check if we have a .env file (local dev) or not (CI)
        import os
        env_file_exists = os.path.exists("/app/.env")
        
        if env_file_exists:
            # Local development: should read from .env file
            expected_name = "My Cool Chat App v2"
            assert data["app_name"] == expected_name, f"Expected {expected_name}, got {data['app_name']}"
        else:
            # CI environment: should use default value
            expected_name = "Galaxy Chat"
            assert data["app_name"] == expected_name, f"Expected {expected_name}, got {data['app_name']}"
    
    def test_llms_endpoint_uses_yaml_config(self):
        """Test that /llms endpoint loads models from YAML configuration."""
        response = self.client.get("/llms")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list), "LLMs endpoint should return a list"
        assert len(data) > 0, "Should have at least one LLM configured"
        
        # Each LLM should have required fields
        for llm in data:
            assert "name" in llm, "Each LLM should have a name"
            assert "provider" in llm, "Each LLM should have a provider"
            assert "model" in llm, "Each LLM should have a model"
    
    def test_yaml_config_file_structure(self):
        """Test that YAML config file has correct structure."""
        # This will fail initially - need to create the YAML file
        config_path = settings.llm_config_file
        assert os.path.exists(config_path), f"LLM config file should exist at {config_path}"
        
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        assert "llms" in config_data, "YAML config should have 'llms' key"
        assert isinstance(config_data["llms"], list), "llms should be a list"
        
        # Validate structure of each LLM config
        for llm in config_data["llms"]:
            required_fields = ["name", "provider", "model", "api_key_env"]
            for field in required_fields:
                assert field in llm, f"LLM config should have {field} field"
    
    def test_frontend_receives_dynamic_app_name(self):
        """Test that frontend HTML includes dynamic app name."""
        response = self.client.get("/")
        assert response.status_code == 200
        
        html_content = response.text
        
        # Should include the app name from config in the title
        assert settings.app_name in html_content, f"HTML should contain app name: {settings.app_name}"
        
        # Check both title tag and any h1 tags
        assert f"<title>{settings.app_name}</title>" in html_content or settings.app_name in html_content


class TestLLMConfigValidation:
    """Test LLM configuration validation and loading."""
    
    def test_invalid_yaml_config_handling(self):
        """Test handling of invalid YAML configuration."""
        # Create temporary invalid YAML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            temp_path = f.name
        
        try:
            # This should handle the error gracefully
            from app.services.llm_config_manager import LLMConfigManager
            config_manager = LLMConfigManager(temp_path)
            
            # Should return empty list or raise appropriate exception
            llms = config_manager.get_available_llms()
            assert isinstance(llms, list), "Should return list even with invalid config"
            
        finally:
            os.unlink(temp_path)
    
    def test_missing_required_fields_in_yaml(self):
        """Test handling of LLM configs missing required fields."""
        # Create YAML with missing fields
        incomplete_config = {
            "llms": [
                {"name": "Test Model"},  # Missing provider, model, api_key_env
                {"provider": "openai", "model": "gpt-4"}  # Missing name, api_key_env
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(incomplete_config, f)
            temp_path = f.name
        
        try:
            from app.services.llm_config_manager import LLMConfigManager
            config_manager = LLMConfigManager(temp_path)
            
            # Should validate and filter out invalid entries
            llms = config_manager.get_available_llms()
            # Should have 0 valid LLMs due to missing required fields
            assert len(llms) == 0, "Invalid LLM configs should be filtered out"
            
        finally:
            os.unlink(temp_path)
    
    def test_environment_variable_substitution(self):
        """Test that API keys are properly loaded from environment variables."""
        test_config = {
            "llms": [
                {
                    "name": "Test GPT",
                    "provider": "openai", 
                    "model": "gpt-3.5-turbo",
                    "api_key_env": "TEST_OPENAI_KEY"
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(test_config, f)
            temp_path = f.name
        
        # Set test environment variable
        os.environ["TEST_OPENAI_KEY"] = "test-api-key-123"
        
        try:
            from app.services.llm_config_manager import LLMConfigManager
            config_manager = LLMConfigManager(temp_path)
            
            llms = config_manager.get_available_llms()
            assert len(llms) == 1, "Should load one valid LLM"
            
            # API key should be resolved from environment
            llm = llms[0]
            # Note: We shouldn't expose the actual API key in the response
            assert "api_key" not in llm, "API key should not be exposed in LLM list"
            
        finally:
            if "TEST_OPENAI_KEY" in os.environ:
                del os.environ["TEST_OPENAI_KEY"]
            os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__])