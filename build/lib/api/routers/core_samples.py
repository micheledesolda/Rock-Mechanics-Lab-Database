# src/api/routers/core_samples.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from src.services.core_sample_service import CoreSampleService

router = APIRouter()
core_sample_service = CoreSampleService()

class CoreSampleCreateRequest(BaseModel):
    core_sample_id: str
    material: str
    dimensions: Dict[str, Any]

@router.post("/", response_model=dict)
def create_core_sample(request: CoreSampleCreateRequest):
    try:
        core_sample_service.create_core_sample(
            core_sample_id=request.core_sample_id,
            material=request.material,
            dimensions=request.dimensions
        )
        return {"message": "Core sample created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{core_sample_id}", response_model=dict)
def get_core_sample(core_sample_id: str):
    try:
        core_sample = core_sample_service.read({"_id": core_sample_id})
        if core_sample:
            return core_sample
        else:
            raise HTTPException(status_code=404, detail="Core sample not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
