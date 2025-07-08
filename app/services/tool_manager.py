
import os
import sys
import importlib.util
import inspect
from typing import Dict, Type, Any, Optional, List
from app.common.base_tool import BaseTool

class ToolManager:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._register_tools()

    def _register_tools(self):
        """Dynamically discover and register tools from the tools folder."""
        tools_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'tools')
        
        if not os.path.exists(tools_folder):
            print(f"Warning: Tools folder not found at {tools_folder}")
            return
        
        # Get all Python files in the tools folder (except base_tool.py)
        tool_files = [
            f for f in os.listdir(tools_folder) 
            if f.endswith('.py') and f != '__init__.py' and f != 'base_tool.py'
        ]
        
        for tool_file in tool_files:
            try:
                self._load_tool_from_file(tools_folder, tool_file)
            except Exception as e:
                print(f"Warning: Failed to load tool from {tool_file}: {e}")
    
    def _load_tool_from_file(self, tools_folder: str, tool_file: str):
        """Load a tool class from a Python file."""
        tool_path = os.path.join(tools_folder, tool_file)
        module_name = tool_file[:-3]  # Remove .py extension
        
        # Load the module
        spec = importlib.util.spec_from_file_location(module_name, tool_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load spec for {tool_file}")
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find all classes that inherit from BaseTool
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if (obj != BaseTool and 
                issubclass(obj, BaseTool) and 
                obj.__module__ == module_name):
                
                # Instantiate and register the tool
                tool_instance = obj()
                self.register_tool(tool_instance)
                print(f"Loaded tool: {tool_instance.get_name()} from {tool_file}")

    def register_tool(self, tool: BaseTool):
        self._tools[tool.get_name()] = tool

    def get_tool(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def get_all_tool_definitions(self) -> List[Dict[str, Any]]:
        definitions = []
        for tool in self._tools.values():
            definitions.append({
                "type": "function",
                "function": {
                    "name": tool.get_name(),
                    "description": tool.get_description(),
                    "parameters": tool.get_parameters()
                }
            })
        return definitions
    
    def reload_tools(self):
        """Reload all tools from the tools folder."""
        self._tools.clear()
        self._register_tools()

tool_manager = ToolManager()
