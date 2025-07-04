from fastapi import APIRouter
from app.services.llm_client import llm_client

router = APIRouter()

@router.get("/api/llm_configs")
async def get_llm_configs():
    return llm_client.llm_config_manager.get_all_llm_configs()