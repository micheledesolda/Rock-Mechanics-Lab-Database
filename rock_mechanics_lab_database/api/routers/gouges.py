# rock_mechanics_lab_database/api/routers/gouges.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from rock_mechanics_lab_database.services.gouge_service import GougeService

router = APIRouter()
gouge_service = GougeService()

class GougeCreateRequest(BaseModel):
    gouge_id: str
    material: str
    grain_size_mum: str

@router.post("/", response_model=dict)
def create_gouge(request: GougeCreateRequest):
    try:
        gouge_service.create_gouge(
            gouge_id=request.gouge_id,
            material=request.material,
            grain_size_mum=request.grain_size_mum
        )
        return {"message": "Gouge created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{gouge_id}", response_model=dict)
def get_gouge(gouge_id: str):
    try:
        gouge = gouge_service.get_gouge(gouge_id)
        if gouge:
            return gouge
        else:
            raise HTTPException(status_code=404, detail="Gouge not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

