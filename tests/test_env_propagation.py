import pytest
import os
import sys
from fastapi.testclient import TestClient

# Add the app directory to the Python path
sys.path.insert(0, '/app')

def test_env_file_app_name_propagates_to_api():
    """Test that the current .env file APP_NAME propagates to the /api/config endpoint."""
    # Import app using the current .env configuration
    from app.main import app
    
    client = TestClient(app)
    
    # Test the API endpoint
    response = client.get("/api/config")
    assert response.status_code == 200
    
    data = response.json()
    assert "app_name" in data
    
    # Should read from the .env file we just updated
    expected_name = "My Cool Chat App v2"
    assert data["app_name"] == expected_name, f"Expected '{expected_name}', got '{data['app_name']}'"

def test_env_file_app_name_propagates_to_frontend():
    """Test that .env APP_NAME is reflected in the frontend title injection."""
    from app.main import app
    
    client = TestClient(app)
    
    # Test the frontend HTML injection
    response = client.get("/")
    assert response.status_code == 200
    
    html_content = response.text
    expected_name = "My Cool Chat App v2"
    assert f"<title>{expected_name}</title>" in html_content, f"Expected title '{expected_name}' not found in HTML"

def test_dynamic_env_variable_override():
    """Test that configuration correctly reads from .env file or environment variables."""
    import tempfile
    import os
    from dotenv import load_dotenv
    
    # Test that current configuration is working correctly
    from app.config import settings
    
    # Check if we have a .env file locally or not (CI environment)
    env_file_exists = os.path.exists("/app/.env")
    
    if env_file_exists:
        # Local development: should read from .env file
        assert settings.app_name == "My Cool Chat App v2", f"Expected 'My Cool Chat App v2', got '{settings.app_name}'"
    else:
        # CI environment: should use default or environment variable
        # Set environment variable and test
        test_app_name = "Dynamic Test App"
        os.environ['APP_NAME'] = test_app_name
        
        try:
            # Create new settings instance
            from app.config import Settings
            fresh_settings = Settings()
            assert fresh_settings.app_name == test_app_name, f"Expected '{test_app_name}', got '{fresh_settings.app_name}'"
        finally:
            # Clean up
            if 'APP_NAME' in os.environ:
                del os.environ['APP_NAME']

if __name__ == "__main__":
    # Run the tests
    test_env_file_app_name_propagates_to_api()
    test_env_file_app_name_propagates_to_frontend() 
    test_dynamic_env_variable_override()
    print("✅ All tests passed!")