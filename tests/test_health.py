from fastapi.testclient import TestClient
from app.main import app, SYSTEM_PROMPT_CONTENT
from app.config import settings
from unittest.mock import patch, MagicMock


def get_fresh_app_client():
    # Re-import app to ensure a fresh state for each test
    import importlib
    import app.main
    import app.config
    
    # Store current settings before reload
    current_settings = {
        'disable_llm_calls': settings.disable_llm_calls,
        'system_prompt_override': settings.system_prompt_override,
    }
    
    print(f"Before get_fresh_app_client: system_prompt_override = {current_settings['system_prompt_override']}")
    print(f"Before get_fresh_app_client: disable_llm_calls = {current_settings['disable_llm_calls']}")
    
    # Reload modules to get fresh state
    importlib.reload(app.config)
    
    # Restore settings immediately after config reload, before main reload
    app.config.settings.disable_llm_calls = current_settings['disable_llm_calls']
    app.config.settings.system_prompt_override = current_settings['system_prompt_override']
    
    importlib.reload(app.main)
    
    # Return TestClient using the reloaded app
    return TestClient(app.main.app)

def test_health_check():
    response = get_fresh_app_client().get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch('app.services.llm_client.LLMClient.chat_completion')
def test_llm_health_check_success(mock_chat_completion):
    mock_chat_completion.return_value.json.return_value = {"choices": [{"message": {"content": "hi"}}]}
    with get_fresh_app_client():
        pass
    mock_chat_completion.assert_called_once_with(messages=[{"role": "user", "content": "hi"}])

@patch('app.services.llm_client.LLMClient.chat_completion')
def test_llm_health_check_failure(mock_chat_completion):
    mock_chat_completion.side_effect = Exception("LLM connection error")
    with get_fresh_app_client():
        pass
    mock_chat_completion.assert_called_once_with(messages=[{"role": "user", "content": "hi"}])

def test_llm_health_check_disabled():
    settings.disable_llm_calls = True
    with patch('app.services.llm_client.LLMClient.chat_completion') as mock_chat_completion:
        with get_fresh_app_client():
            pass
        mock_chat_completion.assert_not_called()
    settings.disable_llm_calls = False

def test_system_prompt_from_file():
    # Temporarily disable LLM calls to prevent hanging during app startup
    original_disable_llm = settings.disable_llm_calls
    settings.disable_llm_calls = True
    settings.system_prompt_override = None
    
    try:
        with patch('builtins.open', new_callable=MagicMock) as mock_open:
            # Configure the file mock
            mock_open.return_value.__enter__.return_value.read.return_value = "Test system prompt from file."
            
            print(f"Before get_fresh_app_client: system_prompt_override = {settings.system_prompt_override}")
            print(f"Before get_fresh_app_client: disable_llm_calls = {settings.disable_llm_calls}")
            
            # Get fresh client which will trigger lifespan
            with get_fresh_app_client():
                # Import the updated SYSTEM_PROMPT_CONTENT from the reloaded module
                import app.main
                print(f"Inside context: SYSTEM_PROMPT_CONTENT = '{app.main.SYSTEM_PROMPT_CONTENT}'")
                print(f"Mock open call count: {mock_open.call_count}")
                print(f"Mock open calls: {mock_open.call_args_list}")
                
                assert app.main.SYSTEM_PROMPT_CONTENT == "Test system prompt from file."
                # Check if the correct file was opened
                system_prompt_calls = [call for call in mock_open.call_args_list if 'system_prompt.md' in str(call)]
                assert len(system_prompt_calls) > 0, f"system_prompt.md was not opened. Calls: {mock_open.call_args_list}"
    finally:
        # Restore original setting
        settings.disable_llm_calls = original_disable_llm

def test_system_prompt_from_override():
    settings.system_prompt_override = "Override system prompt."
    
    with patch('app.services.llm_client.LLMClient.chat_completion') as mock_chat_completion:
        # Mock the LLM health check to prevent hanging
        mock_chat_completion.return_value.json.return_value = {"choices": [{"message": {"content": "hi"}}]}
        
        with get_fresh_app_client() as client:
            # The lifespan should have run by now
            import app.main
            print(f"After client creation: SYSTEM_PROMPT_CONTENT = '{app.main.SYSTEM_PROMPT_CONTENT}'")
            print(f"After client creation: settings.system_prompt_override = '{app.config.settings.system_prompt_override}'")
            assert app.main.SYSTEM_PROMPT_CONTENT == "Override system prompt."

def test_system_prompt_default_if_file_not_found():
    settings.system_prompt_override = None
    
    # Store the original open function
    original_open = open
    
    # Create a mock that only raises FileNotFoundError for system_prompt.md
    def mock_open_side_effect(filename, *args, **kwargs):
        if 'system_prompt.md' in str(filename):
            raise FileNotFoundError(f"No such file or directory: '{filename}'")
        # For other files, use the original open function
        return original_open(filename, *args, **kwargs)
    
    with patch('builtins.open', side_effect=mock_open_side_effect):
        with patch('app.services.llm_client.LLMClient.chat_completion') as mock_chat_completion:
            # Mock the LLM health check to prevent hanging
            mock_chat_completion.return_value.json.return_value = {"choices": [{"message": {"content": "hi"}}]}
            
            with get_fresh_app_client() as client:
                import app.main
                assert app.main.SYSTEM_PROMPT_CONTENT == "You are a helpful AI assistant."
