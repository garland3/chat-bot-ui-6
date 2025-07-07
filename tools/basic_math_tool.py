
from app.common.base_tool import BaseTool
from typing import Dict, Any

class BasicMathTool(BaseTool):
    def get_name(self) -> str:
        return "BasicMathTool"

    def get_description(self) -> str:
        return "Performs basic arithmetic operations like addition, subtraction, multiplication, and division."

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                    "description": "The arithmetic operation to perform."
                },
                "num1": {
                    "type": "number",
                    "description": "The first number."
                },
                "num2": {
                    "type": "number",
                    "description": "The second number."
                }
            },
            "required": ["operation", "num1", "num2"]
        }

    def execute(self, operation: str, num1: float, num2: float) -> Dict[str, Any]:
        if operation == "add":
            result = num1 + num2
        elif operation == "subtract":
            result = num1 - num2
        elif operation == "multiply":
            result = num1 * num2
        elif operation == "divide":
            if num2 == 0:
                return {"error": "Division by zero is not allowed."}
            result = num1 / num2
        else:
            return {"error": "Invalid operation."}
        return {"result": result}
