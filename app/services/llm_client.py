import requests
import json
from app.config import settings
from app.services.tool_manager import tool_manager

class LLMClient:
    def __init__(self):
        self.base_url = settings.llm_base_url
        self.api_key = settings.llm_api_key
        self.model_name = settings.llm_model_name

    def chat_completion(self, messages: list, stream: bool = False, tools: list = None):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": stream
        }
        if tools:
            payload["tools"] = tools

        try:
            response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=payload, stream=stream)
            response.raise_for_status()
            if stream:
                return response.iter_lines()
            return response
        except requests.exceptions.RequestException as e:
            raise Exception(f"LLM API request failed: {e}")

llm_client = LLMClient()