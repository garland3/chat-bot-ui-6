import pytest
import os
import shutil
import sys

# Add the app directory to the Python path
sys.path.insert(0, '/app')

def test_real_world_tool_management_workflow():
    """Test the real-world workflow of adding/removing tools from the tools folder."""
    from app.services.tool_manager import ToolManager
    
    # Initial state - should have 4 tools including UserLookupTool
    tool_manager = ToolManager()
    initial_tools = tool_manager.get_all_tool_definitions()
    initial_names = [tool["function"]["name"] for tool in initial_tools]
    
    print(f"Initial tools: {initial_names}")
    assert "UserLookupTool" in initial_names, f"UserLookupTool should be available now that it's back in tools folder"
    assert "BasicMathTool" in initial_names
    assert "CodeExecutionTool" in initial_names  
    assert "SQLQueryTool" in initial_names
    
    # Test removing a tool (move to temp folder)
    user_tool_path = "/app/tools/user_lookup_tool.py"
    temp_path = "/app/temp_no_tool/user_lookup_tool.py"
    
    # Move tool out
    if os.path.exists(user_tool_path):
        shutil.move(user_tool_path, temp_path)
    
    # Create new tool manager to simulate application restart
    new_tool_manager = ToolManager()
    reduced_tools = new_tool_manager.get_all_tool_definitions()
    reduced_names = [tool["function"]["name"] for tool in reduced_tools]
    
    print(f"Tools after removal: {reduced_names}")
    assert "UserLookupTool" not in reduced_names, "UserLookupTool should not be available after removal"
    assert len(reduced_names) == len(initial_names) - 1, "Should have one less tool"
    
    # Test adding tool back
    if os.path.exists(temp_path):
        shutil.move(temp_path, user_tool_path)
    
    # Create another new tool manager
    restored_tool_manager = ToolManager()
    restored_tools = restored_tool_manager.get_all_tool_definitions()
    restored_names = [tool["function"]["name"] for tool in restored_tools]
    
    print(f"Tools after restoration: {restored_names}")
    assert "UserLookupTool" in restored_names, "UserLookupTool should be available again after restoration"
    assert len(restored_names) == len(initial_names), "Should have all original tools back"

def test_tool_execution_after_dynamic_loading():
    """Test that dynamically loaded tools can actually be executed."""
    from app.services.tool_manager import ToolManager
    
    tool_manager = ToolManager()
    
    # Test BasicMathTool execution
    math_tool = tool_manager.get_tool("BasicMathTool")
    assert math_tool is not None
    result = math_tool.execute(operation="add", num1=5, num2=3)
    assert result["result"] == 8
    
    # Test UserLookupTool execution (if available)
    user_tool = tool_manager.get_tool("UserLookupTool")
    if user_tool is not None:
        result = user_tool.execute(email="john.doe@example.com")
        assert result["status"] == "success"
        assert "John Doe" in str(result)

if __name__ == "__main__":
    test_real_world_tool_management_workflow()
    test_tool_execution_after_dynamic_loading()
    print("✅ All workflow tests passed!")