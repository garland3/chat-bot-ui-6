import requests
import json
from app.config import settings
from app.services.tool_manager import tool_manager
from app.services.llm_config_manager import LLMConfigManager

class LLMClient:
    def __init__(self):
        self.llm_config_manager = LLMConfigManager(settings.llm_config_file)
        self.current_llm_name = "Claude 3.5 Sonnet" # Default LLM
        self._set_current_llm_config()

    def _set_current_llm_config(self):
        config = self.llm_config_manager.get_llm_config(self.current_llm_name)
        self.provider = config.provider.lower()
        self.base_url = config.base_url
        self.api_key = config.api_key
        self.model_name = config.model_name

    def set_llm(self, llm_name: str):
        if llm_name not in self.llm_config_manager.get_all_llm_names():
            raise ValueError(f"LLM '{llm_name}' not found in configuration.")
        self.current_llm_name = llm_name
        self._set_current_llm_config()

    def get_available_llms(self):
        return self.llm_config_manager.get_all_llm_names()

    def chat_completion(self, messages: list, stream: bool = False, tools: list = None):
        if self.provider == "anthropic":
            return self._anthropic_chat_completion(messages, stream, tools)
        elif self.provider == "openai":
            return self._openai_chat_completion(messages, stream, tools)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def _openai_chat_completion(self, messages: list, stream: bool = False, tools: list = None):
        """OpenAI API implementation"""
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
            raise Exception(f"OpenAI API request failed: {e}")

    def _anthropic_chat_completion(self, messages: list, stream: bool = False, tools: list = None):
        """Anthropic API implementation"""
        # Convert OpenAI format messages to Anthropic format
        anthropic_messages = []
        system_message = None
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            elif msg["role"] == "user":
                anthropic_messages.append({
                    "role": "user",
                    "content": msg["content"]
                })
            elif msg["role"] == "assistant":
                anthropic_messages.append({
                    "role": "assistant", 
                    "content": msg.get("content", "")
                })
            elif msg["role"] == "tool":
                # For tool responses, we'll append to the last assistant message
                if anthropic_messages and anthropic_messages[-1]["role"] == "assistant":
                    anthropic_messages[-1]["content"] += f"\n\nTool result: {msg['content']}"

        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": self.model_name,
            "messages": anthropic_messages,
            "max_tokens": 1000,
            "stream": stream
        }
        
        if system_message:
            payload["system"] = system_message

        try:
            response = requests.post(f"{self.base_url}/messages", headers=headers, json=payload, stream=stream)
            response.raise_for_status()
            
            if stream:
                return self._anthropic_stream_wrapper(response.iter_lines())
            else:
                # Convert Anthropic response format to OpenAI-like format for compatibility
                anthropic_response = response.json()
                openai_format = {
                    "choices": [{
                        "message": {
                            "role": "assistant",
                            "content": anthropic_response.get("content", [{}])[0].get("text", "")
                        }
                    }]
                }
                
                # Create a mock response object with json() method
                class MockResponse:
                    def __init__(self, data):
                        self.data = data
                    def json(self):
                        return self.data
                
                return MockResponse(openai_format)
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Anthropic API request failed: {e}")

    def _anthropic_stream_wrapper(self, stream):
        """Convert Anthropic streaming format to OpenAI-like format"""
        for line in stream:
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])
                        if data.get('type') == 'content_block_delta':
                            # Convert to OpenAI-like streaming format
                            openai_chunk = {
                                "choices": [{
                                    "delta": {
                                        "content": data.get('delta', {}).get('text', '')
                                    }
                                }]
                            }
                            yield f"data: {json.dumps(openai_chunk)}\n\n".encode('utf-8')
                        elif data.get('type') == 'message_stop':
                            yield b"data: [DONE]\n\n"
                    except json.JSONDecodeError:
                        continue

llm_client = LLMClient()
