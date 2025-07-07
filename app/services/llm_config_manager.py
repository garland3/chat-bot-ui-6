from typing import List, Dict, Any, Optional
import yaml
import os
from pydantic import BaseModel, Field

class LLMConfig(BaseModel):
    name: str
    provider: str
    model: str
    api_key_env: str
    base_url: Optional[str] = None
    description: Optional[str] = None
    api_key: Optional[str] = None  # Resolved at runtime

class LLMConfigPublic(BaseModel):
    name: str
    provider: str
    model: str
    description: Optional[str] = None

class LLMConfigManager:
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.llm_configs: Dict[str, LLMConfig] = {}
        self._load_configs()

    def _load_configs(self):
        """Load LLM configurations from YAML file."""
        if not os.path.exists(self.config_file):
            print(f"Warning: LLM configuration file not found: {self.config_file}")
            return

        try:
            with open(self.config_file, 'r') as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file {self.config_file}: {e}")
            return
        
        if not data or 'llms' not in data or not isinstance(data['llms'], list):
            print(f"Invalid LLM configuration format in {self.config_file}: 'llms' key missing or not a list")
            return

        for config_data in data['llms']:
            try:
                # Validate required fields
                required_fields = ['name', 'provider', 'model', 'api_key_env']
                if not all(field in config_data for field in required_fields):
                    print(f"Skipping invalid LLM config missing required fields: {config_data}")
                    continue

                # Resolve API key from environment variable
                api_key_env = config_data['api_key_env']
                api_key = os.getenv(api_key_env)
                if not api_key:
                    print(f"Warning: API key environment variable '{api_key_env}' not set for {config_data['name']}")
                
                config_data['api_key'] = api_key
                llm_config = LLMConfig(**config_data)
                self.llm_configs[llm_config.name] = llm_config
                
            except Exception as e:
                print(f"Error loading LLM config {config_data}: {e}")
                continue

    def get_llm_config(self, name: str) -> LLMConfig:
        """Get LLM configuration by name."""
        if name not in self.llm_configs:
            raise ValueError(f"LLM configuration '{name}' not found.")
        return self.llm_configs[name]

    def get_all_llm_names(self) -> List[str]:
        """Get list of all LLM names."""
        return list(self.llm_configs.keys())

    def get_available_llms(self) -> List[LLMConfigPublic]:
        """Get all available LLM configurations (without sensitive data)."""
        return [
            LLMConfigPublic(
                name=config.name,
                provider=config.provider, 
                model=config.model,
                description=config.description
            ) 
            for config in self.llm_configs.values()
        ]

    def reload_configs(self):
        """Reload configurations from file."""
        self.llm_configs.clear()
        self._load_configs()
