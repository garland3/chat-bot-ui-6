"""
System Prompt Engine for dynamic prompt generation based on tool and data source selections.
"""
import os
from typing import List, Optional
from app.config import settings


class SystemPromptEngine:
    def __init__(self):
        self.base_prompt = None  # Load lazily to avoid circular imports
        
    def _load_base_prompt(self) -> str:
        """Load base system prompt from various sources with fallback."""
        # Priority 1: Environment override
        if settings.system_prompt_override:
            return settings.system_prompt_override
            
        # Priority 2: Global loaded content (avoid circular import)
        try:
            import app.main
            if hasattr(app.main, 'SYSTEM_PROMPT_CONTENT') and app.main.SYSTEM_PROMPT_CONTENT:
                return app.main.SYSTEM_PROMPT_CONTENT
        except ImportError:
            pass
            
        # Priority 3: Read from file
        try:
            with open("system_prompt.md", "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            pass
            
        # Priority 4: Default fallback
        return "You are a helpful AI assistant."
    
    def _get_base_prompt(self) -> str:
        """Get base prompt, loading lazily if needed."""
        if self.base_prompt is None:
            self.base_prompt = self._load_base_prompt()
        return self.base_prompt
    
    def generate_system_prompt(self, 
                             selected_tools: Optional[List[str]] = None, 
                             selected_data_sources: Optional[List[str]] = None) -> str:
        """Generate complete system prompt based on selections."""
        prompt_parts = [self._get_base_prompt()]
        
        # Add data sources context
        if selected_data_sources:
            data_context = self._generate_data_sources_context(selected_data_sources)
            if data_context:
                prompt_parts.append(data_context)
        
        # Add tool capabilities
        if selected_tools:
            tool_context = self._generate_tools_context(selected_tools)
            if tool_context:
                prompt_parts.append(tool_context)
        
        return "\n\n".join(prompt_parts)
    
    def _generate_data_sources_context(self, data_sources: List[str]) -> str:
        """Generate context for selected data sources."""
        if not data_sources:
            return ""
            
        context = "You have access to the following data sources: " + ", ".join(data_sources)
        
        # Add specific guidance for known data sources
        data_source_guidance = []
        
        if "employees" in data_sources:
            data_source_guidance.append("employees (staff directory and organizational information)")
        if "products" in data_sources:
            data_source_guidance.append("products (product catalog and specifications)")
        if "orders" in data_sources:
            data_source_guidance.append("orders (order history and transaction data)")
        
        if data_source_guidance:
            context += ": " + ", ".join(data_source_guidance)
        
        return context
    
    def _generate_tools_context(self, tools: List[str]) -> str:
        """Generate context for selected tools."""
        if not tools:
            return ""
            
        tool_contexts = []
        
        for tool in tools:
            if tool == "calculator":
                tool_contexts.append(
                    "You have access to a calculator and should use it for any mathematical "
                    "calculations. Frame your thinking process around calculations and show "
                    "your mathematical reasoning clearly."
                )
            elif tool == "code_execution":
                tool_contexts.append(
                    "You have access to code execution capabilities. You can discuss code "
                    "examples and programming concepts with confidence."
                )
            elif tool == "user_lookup":
                tool_contexts.append(
                    "You have access to user lookup capabilities for organizational "
                    "information and staff directories."
                )
            elif tool == "sql_query":
                tool_contexts.append(
                    "You have access to database query capabilities for retrieving "
                    "structured data and generating reports."
                )
        
        return "\n".join(tool_contexts) if tool_contexts else ""


# Global instance
system_prompt_engine = SystemPromptEngine()