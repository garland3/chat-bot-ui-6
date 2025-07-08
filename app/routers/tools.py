"""
API endpoints for available tools and data sources.
"""
from fastapi import APIRouter
from typing import List, Dict, Any
from app.services.tool_manager import tool_manager

router = APIRouter()

# Available data sources configuration
AVAILABLE_DATA_SOURCES = [
    {
        "id": "data-test",
        "name": "Test Data Source",
        "description": "A simple test data source for demonstration purposes",
        "category": "testing"
    },
    {
        "id": "new-mexico-history",
        "name": "New Mexico History",
        "description": "Historical information and facts about the state of New Mexico",
        "category": "historical"
    }
]

@router.get("/api/tools")
async def get_available_tools() -> Dict[str, List[Dict[str, Any]]]:
    """Get list of available tools."""
    tools = []
    for tool_name, tool_instance in tool_manager._tools.items():
        tools.append({
            "id": tool_name.lower().replace("tool", ""),
            "name": tool_name,
            "description": tool_instance.get_description(),
            "category": "dynamic"
        })
    return {"tools": tools}

@router.get("/api/data-sources") 
async def get_available_data_sources() -> Dict[str, List[Dict[str, Any]]]:
    """Get list of available data sources."""
    return {"data_sources": AVAILABLE_DATA_SOURCES}