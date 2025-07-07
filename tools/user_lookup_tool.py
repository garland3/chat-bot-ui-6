
from app.common.base_tool import BaseTool
from typing import Dict, Any

class UserLookupTool(BaseTool):
    def get_name(self) -> str:
        return "UserLookupTool"

    def get_description(self) -> str:
        return "Looks up user information in a corporate directory."

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "description": "The email address of the user to look up."
                }
            },
            "required": ["email"]
        }

    def execute(self, email: str) -> Dict[str, Any]:
        # Sample user data
        users = {
            "john.doe@example.com": {"name": "John Doe", "title": "Software Engineer", "department": "Engineering"},
            "jane.smith@example.com": {"name": "Jane Smith", "title": "Product Manager", "department": "Product"},
            "peter.jones@example.com": {"name": "Peter Jones", "title": "HR Specialist", "department": "Human Resources"},
        }
        user_info = users.get(email.lower())
        if user_info:
            return {"user_info": user_info, "status": "success"}
        else:
            return {"error": "User not found.", "status": "failure"}
