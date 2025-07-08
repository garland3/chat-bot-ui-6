"""
Tests for tools and data sources API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_available_tools():
    """Test the /api/tools endpoint returns available tools."""
    response = client.get("/api/tools")
    assert response.status_code == 200
    
    data = response.json()
    assert "tools" in data
    assert isinstance(data["tools"], list)
    assert len(data["tools"]) > 0
    
    # Check structure of first tool
    tool = data["tools"][0]
    assert "id" in tool
    assert "name" in tool  
    assert "description" in tool
    assert "category" in tool
    
    # Check for expected tools (now dynamically loaded)
    tool_ids = [tool["id"] for tool in data["tools"]]
    tool_names = [tool["name"] for tool in data["tools"]]
    
    # Check that we have the expected dynamic tools
    assert "basicmath" in tool_ids or "BasicMathTool" in tool_names
    assert "codeexecution" in tool_ids or "CodeExecutionTool" in tool_names
    assert "userlookup" in tool_ids or "UserLookupTool" in tool_names

def test_get_available_data_sources():
    """Test the /api/data-sources endpoint returns available data sources."""
    response = client.get("/api/data-sources")
    assert response.status_code == 200
    
    data = response.json()
    assert "data_sources" in data
    assert isinstance(data["data_sources"], list)
    assert len(data["data_sources"]) > 0
    
    # Check structure of first data source
    data_source = data["data_sources"][0]
    assert "id" in data_source
    assert "name" in data_source
    assert "description" in data_source
    assert "category" in data_source
    
    # Check for expected data sources (updated to new test sources)
    data_source_ids = [ds["id"] for ds in data["data_sources"]]
    assert "data-test" in data_source_ids
    assert "new-mexico-history" in data_source_ids

def test_tools_endpoint_structure():
    """Test that tools have consistent structure."""
    response = client.get("/api/tools")
    data = response.json()
    
    for tool in data["tools"]:
        # All tools should have required fields
        assert isinstance(tool["id"], str)
        assert isinstance(tool["name"], str)
        assert isinstance(tool["description"], str)
        assert isinstance(tool["category"], str)
        assert len(tool["id"]) > 0
        assert len(tool["name"]) > 0

def test_data_sources_endpoint_structure():
    """Test that data sources have consistent structure."""
    response = client.get("/api/data-sources")
    data = response.json()
    
    for data_source in data["data_sources"]:
        # All data sources should have required fields
        assert isinstance(data_source["id"], str)
        assert isinstance(data_source["name"], str)
        assert isinstance(data_source["description"], str)
        assert isinstance(data_source["category"], str)
        assert len(data_source["id"]) > 0
        assert len(data_source["name"]) > 0