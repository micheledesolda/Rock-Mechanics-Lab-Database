# src/
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional

router = APIRouter()

class Gouge(BaseModel):
    gouge_id: str

class Block(BaseModel):
    block_id: str

class ExperimentCreate(BaseModel):
    experiment_id: str
    experiment_type: str
    gouges: List[Gouge]
    core_sample_id: Optional[str]
    blocks: List[Block]

@router.post("/create")
async def create_experiment(experiment: ExperimentCreate):
    try:
        experiment_id = experiment_dao.create_experiment(
            experiment_id=experiment.experiment_id,
            experiment_type=experiment.experiment_type,
            gouges=[gouge.dict() for gouge in experiment.gouges],
            core_sample_id=experiment.core_sample_id,
            blocks=[block.dict() for block in experiment.blocks]
        )
        if not experiment_id:
            raise HTTPException(status_code=500, detail="Experiment creation failed")
        return {"message": f"Experiment {experiment_id} created successfully"}
    except Exception as e:
        print(f"Error creating experiment: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.get("/options")
async def get_options():
    # Mock data for options
    options = {
        "gouges": [{"id": "gouge1", "name": "Gouge 1"}, {"id": "gouge2", "name": "Gouge 2"}],
        "core_sample_ids": [{"id": "sample1", "name": "Sample 1"}, {"id": "sample2", "name": "Sample 2"}],
        "blocks": [{"id": "block1", "name": "Block 1"}, {"id": "block2", "name": "Block 2"}]
    }
    return options
