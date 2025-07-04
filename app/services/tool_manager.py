
from typing import Dict, Type, Any, Optional, List
from tools.base_tool import BaseTool
from tools.basic_math_tool import BasicMathTool
from tools.code_execution_tool import CodeExecutionTool
from tools.user_lookup_tool import UserLookupTool
from tools.sql_query_tool import SQLQueryTool

class ToolManager:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._register_tools()

    def _register_tools(self):
        self.register_tool(BasicMathTool())
        self.register_tool(CodeExecutionTool())
        self.register_tool(UserLookupTool())
        self.register_tool(SQLQueryTool())

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

tool_manager = ToolManager()
