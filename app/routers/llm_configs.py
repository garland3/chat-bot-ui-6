from fastapi import APIRouter
from typing import List
from app.services.llm_client import llm_client
from app.services.llm_config_manager import LLMConfigPublic

router = APIRouter()

@router.get("/api/llm_configs", response_model=List[LLMConfigPublic])
async def get_llm_configs():
    return llm_client.llm_config_manager.get_all_llm_configs()