# rock_mechanics_lab_database/api/routers/machines.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from rock_mechanics_lab_database.services.machine_service import MachineService

router = APIRouter()
machine_service = MachineService()

class MachineCreateRequest(BaseModel):
    machine_id: str
    machine_type: str
    pistons: Dict[str, Any]

class PistonCalibrationRequest(BaseModel):
    piston_name: str
    calibration: Dict[str, Any]
    calibration_date: str

class StiffnessCalibrationRequest(BaseModel):
    piston_name: str
    stiffness: Dict[str, Any]
    stiffness_date: str

class CalibrationApplyRequest(BaseModel):
    piston_name: str
    voltage: float
    experiment_id: str

class StiffnessApplyRequest(BaseModel):
    piston_name: str
    force: float
    experiment_id: str

@router.post("/", response_model=dict)
def create_machine(request: MachineCreateRequest):
    try:
        machine_service.create_machine(
            machine_id=request.machine_id,
            machine_type=request.machine_type,
            pistons=request.pistons
        )
        return {"message": "Machine created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{machine_id}", response_model=dict)
def get_machine(machine_id: str):
    try:
        machine = machine_service.get_machine_by_id(machine_id)
        if machine:
            return machine
        else:
            raise HTTPException(status_code=404, detail="Machine not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{machine_id}", response_model=dict)
def update_machine(machine_id: str, update_fields: Dict[str, Any]):
    try:
        machine_service.update_machine(machine_id, update_fields)
        return {"message": "Machine updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{machine_id}", response_model=dict)
def delete_machine(machine_id: str):
    try:
        machine_service.delete_machine(machine_id)
        return {"message": "Machine deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{machine_id}/calibration", response_model=dict)
def add_piston_calibration(machine_id: str, request: PistonCalibrationRequest):
    try:
        machine_service.add_piston_calibration(
            machine_id=machine_id,
            piston_name=request.piston_name,
            calibration=request.calibration,
            calibration_date=request.calibration_date
        )
        return {"message": "Piston calibration added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{machine_id}/stiffness", response_model=dict)
def add_stiffness_calibration(machine_id: str, request: StiffnessCalibrationRequest):
    try:
        machine_service.add_stiffness_calibration(
            machine_id=machine_id,
            piston_name=request.piston_name,
            stiffness=request.stiffness,
            stiffness_date=request.stiffness_date
        )
        return {"message": "Stiffness calibration added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{machine_id}/apply_calibration", response_model=dict)
def apply_calibration(machine_id: str, request: CalibrationApplyRequest):
    try:
        result = machine_service.apply_calibration(
            machine_id=machine_id,
            piston_name=request.piston_name,
            voltage=request.voltage,
            experiment_date=request.experiment_id  # ensure correct parameter name
        )
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{machine_id}/apply_stiffness", response_model=dict)
def apply_stiffness(machine_id: str, request: StiffnessApplyRequest):
    try:
        result = machine_service.apply_stiffness_correction(
            machine_id=machine_id,
            piston_name=request.piston_name,
            force=request.force,
            experiment_date=request.experiment_id  # ensure correct parameter name
        )
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
