import pytest
import os
import sys
import tempfile
import shutil
from unittest.mock import patch
from fastapi.testclient import TestClient

# Add the app directory to the Python path
sys.path.insert(0, '/app')

def test_tools_folder_auto_discovery():
    """Test that tools are automatically discovered from the tools folder."""
    from app.services.tool_manager import ToolManager
    
    # Create a fresh tool manager
    tool_manager = ToolManager()
    
    # Should discover tools from the tools folder
    tools = tool_manager.get_all_tool_definitions()
    tool_names = [tool["function"]["name"] for tool in tools]
    
    # Should find existing tools (including user_lookup_tool which is back in tools folder)
    expected_tools = ["BasicMathTool", "CodeExecutionTool", "UserLookupTool"]
    for expected_tool in expected_tools:
        assert expected_tool in tool_names, f"Expected tool '{expected_tool}' not found in {tool_names}"

def test_adding_tool_to_folder_makes_it_available():
    """Test that adding a tool to the tools folder makes it available."""
    from app.services.tool_manager import ToolManager
    import pytest
    
    # Skip this test in CI environments where we can't write to /app
    if not os.access("/app", os.W_OK):
        pytest.skip("Skipping dynamic tool test in read-only environment (CI)")
    
    # Create a test tool file in the tools folder
    test_tool_content = '''
from app.common.base_tool import BaseTool
from typing import Dict, Any

class TestDynamicTool(BaseTool):
    def get_name(self) -> str:
        return "TestDynamicTool"

    def get_description(self) -> str:
        return "A test tool for dynamic loading."

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "test_param": {
                    "type": "string",
                    "description": "A test parameter."
                }
            },
            "required": ["test_param"]
        }

    def execute(self, test_param: str) -> Dict[str, Any]:
        return {"result": f"Test executed with: {test_param}"}
'''
    
    test_tool_path = "/app/tools/test_dynamic_tool.py"
    
    try:
        # Ensure tools directory exists
        os.makedirs("/app/tools", exist_ok=True)
        
        # Write the test tool
        with open(test_tool_path, 'w') as f:
            f.write(test_tool_content)
        
        # Create a fresh tool manager that should discover the new tool
        tool_manager = ToolManager()
        tool_manager.reload_tools()  # Force reload to pick up new tool
        tools = tool_manager.get_all_tool_definitions()
        tool_names = [tool["function"]["name"] for tool in tools]
        
        # Should find our new test tool
        assert "TestDynamicTool" in tool_names, f"TestDynamicTool not found in {tool_names}"
        
        # Should be able to get and execute the tool
        test_tool = tool_manager.get_tool("TestDynamicTool")
        assert test_tool is not None
        result = test_tool.execute(test_param="hello")
        assert result["result"] == "Test executed with: hello"
        
    finally:
        # Clean up
        if os.path.exists(test_tool_path):
            os.remove(test_tool_path)

def test_removing_tool_from_folder_makes_it_unavailable():
    """Test that tools automatically removed from folder are not available."""
    from app.services.tool_manager import ToolManager
    import pytest
    import shutil
    
    # Skip this test in CI environments where we can't write to /app
    if not os.access("/app", os.W_OK):
        pytest.skip("Skipping dynamic tool test in read-only environment (CI)")
    
    # First, move UserLookupTool out temporarily
    user_tool_path = "/app/tools/user_lookup_tool.py"
    temp_path = "/app/temp_no_tool/user_lookup_tool_temp.py"
    
    # Ensure directories exist
    os.makedirs("/app/tools", exist_ok=True)
    os.makedirs("/app/temp_no_tool", exist_ok=True)
    
    if os.path.exists(user_tool_path):
        shutil.move(user_tool_path, temp_path)
    
    try:
        # Create tool manager without UserLookupTool
        tool_manager = ToolManager()
        tool_manager.reload_tools()  # Force reload to pick up changes
        tools = tool_manager.get_all_tool_definitions()
        tool_names = [tool["function"]["name"] for tool in tools]
        
        # UserLookupTool should not be available since it was moved out
        assert "UserLookupTool" not in tool_names
        
        # Should not be able to get the removed tool
        user_tool = tool_manager.get_tool("UserLookupTool")
        assert user_tool is None
        
    finally:
        # Restore the tool
        if os.path.exists(temp_path):
            shutil.move(temp_path, user_tool_path)

def test_tools_api_endpoint_reflects_dynamic_changes():
    """Test that the /api/tools endpoint reflects dynamically loaded tools."""
    from app.main import app
    
    client = TestClient(app)
    response = client.get("/api/tools")
    assert response.status_code == 200
    
    data = response.json()
    tool_names = [tool["name"] for tool in data["tools"]]
    
    # Should reflect current tools folder contents
    expected_tools = ["BasicMathTool", "CodeExecutionTool", "UserLookupTool"]
    for expected_tool in expected_tools:
        assert expected_tool in tool_names

if __name__ == "__main__":
    # Run the failing tests first
    test_tools_folder_auto_discovery()
    test_adding_tool_to_folder_makes_it_available()
    test_removing_tool_from_folder_makes_it_unavailable()
    test_tools_api_endpoint_reflects_dynamic_changes()
    print("✅ All tests passed!")