# src/api/routers/experiments.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from src.services.experiment_service import ExperimentService

router = APIRouter()
experiment_service = ExperimentService()

class Gouge(BaseModel):
    gouge_id: str

class Block(BaseModel):
    block_id: str

class ExperimentCreateRequest(BaseModel):
    experiment_id: str
    experiment_type: str
    gouges: List[Gouge]
    core_sample_id: str
    blocks: List[Block]
    centralized_measurements: List[Dict]
    additional_measurements: List[Dict]

@router.post("/", response_model=dict)
def create_experiment(request: ExperimentCreateRequest):
    try:
        experiment_service.create_experiment(
            experiment_id=request.experiment_id,
            experiment_type=request.experiment_type,
            gouges=[g.model_dump() for g in request.gouges],
            core_sample_id=request.core_sample_id,
            blocks=[b.model_dump() for b in request.blocks],
            centralized_measurements=request.centralized_measurements,
            additional_measurements=request.additional_measurements
        )
        return {"message": f"Experiment {request.experiment_id} created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{experiment_id}", response_model=dict)
def get_experiment(experiment_id: str):
    try:
        experiment = experiment_service.get_experiment_by_id(experiment_id)
        if experiment:
            return experiment
        else:
            raise HTTPException(status_code=404, detail="Experiment not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
