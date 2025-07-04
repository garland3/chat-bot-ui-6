from typing import List, Dict, Any
import yaml
import os
from pydantic import BaseModel, Field

class LLMConfig(BaseModel):
    name: str
    provider: str
    base_url: str
    api_key: str
    model_name: str

class LLMConfigManager:
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.llm_configs: Dict[str, LLMConfig] = {}
        self._load_configs()

    def _load_configs(self):
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"LLM configuration file not found: {self.config_file}")

        with open(self.config_file, 'r') as f:
            data = yaml.safe_load(f)
        
        if 'llms' not in data or not isinstance(data['llms'], list):
            raise ValueError("Invalid LLM configuration format: 'llms' key missing or not a list")

        for config_data in data['llms']:
            # Resolve environment variables in api_key and base_url
            for key in ["api_key", "base_url"]:
                if isinstance(config_data.get(key), str) and config_data[key].startswith("${") and config_data[key].endswith("}"):
                    env_var = config_data[key][2:-1]
                    config_data[key] = os.getenv(env_var, "")

            llm_config = LLMConfig(**config_data)
            self.llm_configs[llm_config.name] = llm_config

    def get_llm_config(self, name: str) -> LLMConfig:
        if name not in self.llm_configs:
            raise ValueError(f"LLM configuration '{name}' not found.")
        return self.llm_configs[name]

    def get_all_llm_names(self) -> List[str]:
        return list(self.llm_configs.keys())
