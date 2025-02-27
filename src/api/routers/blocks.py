# src/api/routers/experiments.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from services.block_service import BlockService

router = APIRouter()
block_service = BlockService()

class BlockCreateRequest(BaseModel):
    block_id: str
    material: str
    dimensions: Dict[str, float]
    sensor_rail_width: float
    sensors: List[Dict] = []

@router.post("/", response_model=dict)
def create_block(request: BlockCreateRequest):
    try:
        block_service.create_block(
            block_id=request.block_id,
            material=request.material,
            dimensions=request.dimensions,
            sensor_rail_width=request.sensor_rail_width,
            sensors=request.sensors
        )
        return {"message": "Block created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{block_id}", response_model=dict)
def get_block(block_id: str):
    try:
        block = block_service.get_block(block_id)
        if block:
            return block
        else:
            raise HTTPException(status_code=404, detail="Block not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
