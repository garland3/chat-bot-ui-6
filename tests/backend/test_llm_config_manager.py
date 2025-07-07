import pytest
import os
from app.services.llm_config_manager import LLMConfigManager, LLMConfig

# Mock environment variables for testing
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "mock_openai_key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "mock_anthropic_key")
    monkeypatch.setenv("OLLAMA_API_KEY", "mock_ollama_key")

@pytest.fixture
def mock_llm_config_file(tmp_path):
    config_content = """
llms:
  - name: "Test OpenAI GPT-3.5"
    provider: "openai"
    base_url: "https://api.testopenai.com/v1"
    api_key_env: "OPENAI_API_KEY"
    model: "gpt-3.5-turbo-test"
    description: "Test OpenAI model"
    
  - name: "Test Anthropic Claude"
    provider: "anthropic"
    base_url: "https://api.testanthropic.com"
    api_key_env: "ANTHROPIC_API_KEY"
    model: "claude-test"
    description: "Test Anthropic model"
    
  - name: "Local Test Ollama"
    provider: "ollama"
    base_url: "http://localhost:11434/v1"
    api_key_env: "OLLAMA_API_KEY"
    model: "llama2-test"
    description: "Test Ollama model"
"""
    config_file = tmp_path / "test_llms.yml"
    config_file.write_text(config_content)
    return str(config_file)

def test_llm_config_manager_loads_configs(mock_llm_config_file):
    manager = LLMConfigManager(mock_llm_config_file)
    assert len(manager.llm_configs) == 3
    assert "Test OpenAI GPT-3.5" in manager.llm_configs
    assert "Test Anthropic Claude" in manager.llm_configs
    assert "Local Test Ollama" in manager.llm_configs

def test_llm_config_manager_resolves_env_vars(mock_llm_config_file):
    manager = LLMConfigManager(mock_llm_config_file)
    openai_config = manager.get_llm_config("Test OpenAI GPT-3.5")
    anthropic_config = manager.get_llm_config("Test Anthropic Claude")
    ollama_config = manager.get_llm_config("Local Test Ollama")

    assert openai_config.api_key == "mock_openai_key"
    assert anthropic_config.api_key == "mock_anthropic_key"
    assert ollama_config.api_key == "mock_ollama_key"

def test_llm_config_manager_get_llm_config(mock_llm_config_file):
    manager = LLMConfigManager(mock_llm_config_file)
    config = manager.get_llm_config("Test OpenAI GPT-3.5")
    assert isinstance(config, LLMConfig)
    assert config.name == "Test OpenAI GPT-3.5"
    assert config.provider == "openai"
    assert config.base_url == "https://api.testopenai.com/v1"
    assert config.model == "gpt-3.5-turbo-test"

def test_llm_config_manager_get_all_llm_names(mock_llm_config_file):
    manager = LLMConfigManager(mock_llm_config_file)
    names = manager.get_all_llm_names()
    assert sorted(names) == sorted(["Test OpenAI GPT-3.5", "Test Anthropic Claude", "Local Test Ollama"])

def test_llm_config_manager_file_not_found():
    # Manager should handle missing files gracefully, not raise exceptions
    manager = LLMConfigManager("non_existent_file.yml")
    assert len(manager.llm_configs) == 0

def test_llm_config_manager_invalid_format(tmp_path):
    invalid_config_file = tmp_path / "invalid_llms.yml"
    invalid_config_file.write_text("not_llms: []")
    # Manager should handle invalid format gracefully, not raise exceptions
    manager = LLMConfigManager(str(invalid_config_file))
    assert len(manager.llm_configs) == 0

def test_llm_config_manager_llm_not_found(mock_llm_config_file):
    manager = LLMConfigManager(mock_llm_config_file)
    with pytest.raises(ValueError, match="LLM configuration 'NonExistentLLM' not found."):
        manager.get_llm_config("NonExistentLLM")
