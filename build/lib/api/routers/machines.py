# src/api/routers/machines.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from src.services.machine_service import MachineService

router = APIRouter()
machine_service = MachineService()

class MachineCreateRequest(BaseModel):
    machine_id: str
    properties: Dict[str, Any]
    pistons: str

@router.post("/", response_model=dict)
def create_machine(request: MachineCreateRequest):
    try:
        machine_service.create_machine(
            machine_id=request.machine_id,
            properties=request.properties,
            pistons=request.pistons
        )
        return {"message": "Machine created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{machine_id}", response_model=dict)
def get_machine(machine_id: str):
    try:
        machine = machine_service.read({"_id": machine_id})
        if machine:
            return machine
        else:
            raise HTTPException(status_code=404, detail="Machine not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
