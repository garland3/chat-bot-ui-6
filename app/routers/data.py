
from fastapi import APIRouter, Request, HTTPException
from typing import List, Dict, Any
from app.config import settings

router = APIRouter()

@router.get("/data/{data_source_name}", response_model=List[Dict[str, Any]])
async def get_data(data_source_name: str, request: Request):
    # Placeholder for data source access control
    # In a real application, you would check user permissions here
    user_email = request.state.user_email

    if data_source_name == "customers":
        return [
            {"id": 1, "name": "Alice Smith", "email": "alice@example.com"},
            {"id": 2, "name": "Bob Johnson", "email": "bob@example.com"},
        ]
    elif data_source_name == "products":
        return [
            {"id": 101, "name": "Laptop", "price": 1200.00},
            {"id": 102, "name": "Mouse", "price": 25.00},
        ]
    else:
        raise HTTPException(status_code=404, detail="Data source not found")

@router.get("/app_settings")
async def get_app_settings():
    return {"app_name": settings.app_name}
