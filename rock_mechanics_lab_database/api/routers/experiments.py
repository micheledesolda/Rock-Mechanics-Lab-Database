# rock_mechanics_lab_database/api/routers/experiments.py

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from services.experiment_service import ExperimentService
from scripts.reduction_script import (
    process_vertical_load_measurements,
    process_horizontal_load_measurements,
    process_load_point_displacement,
    process_layer_thickness,
    calculate_gouge_area_from_blocks_dimensions,
    synchronization_to_ultrasonic_waveforms
)
import csv

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

class ExperimentReductionRequest(BaseModel):
    experiment_id: str
    machine_id: str
    layer_thickness_measured_mm: Optional[float] = None
    layer_thickness_measured_point: Optional[int] = 0

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

@router.get("/{experiment_id}/measurements", response_model=List[str])
async def get_adc_channel_names(experiment_id: str):
    try:
        measurements = experiment_service.get_centralized_measurements(experiment_id, "ADC", "All")
        channel_names = list(measurements.keys())
        if not channel_names:
            raise HTTPException(status_code=404, detail="No ADC channels found for the experiment")
        return channel_names
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/experiments/all_ids", response_model=List[str])
async def get_all_experiment_ids():
    try:
        experiment_ids = experiment_service.get_all_experiment_ids()
        if not experiment_ids:
            raise HTTPException(status_code=404, detail="No experiments found")
        return experiment_ids
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_experiment_from_file")
async def create_experiment_from_file(file: UploadFile = File(...)):
    try:
        file_location = f"/tmp/{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())
        experiment_id = experiment_service.create_experiment_from_file(file_location)
        return {"experiment_id": experiment_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{experiment_id}/add_centralized_measurements")
async def add_centralized_measurements(experiment_id: str, file: UploadFile = File(...)):
    try:
        file_location = f"/tmp/{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())
        success = experiment_service.add_centralized_measurements_from_tdms_file(experiment_id, file_location)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{experiment_id}/process_vertical_load", response_model=dict)
async def process_vertical_load(data: ExperimentReductionRequest):
    try:
        experiment_info = experiment_service.get_experiment_by_id(data.experiment_id)
        if not experiment_info:
            raise HTTPException(status_code=404, detail="Experiment not found")
        
        experiment_date = experiment_info['Start_Datetime']
        gouge_area = calculate_gouge_area_from_blocks_dimensions(experiment_id=data.experiment_id)
        
        shear_stress_MPa = process_vertical_load_measurements(
            experiment_id=data.experiment_id,
            machine_id=data.machine_id,
            experiment_date=experiment_date,
            gouge_area=gouge_area
        )
        
        return {"shear_stress_MPa": shear_stress_MPa.tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{experiment_id}/process_horizontal_load", response_model=dict)
async def process_horizontal_load(data: ExperimentReductionRequest):
    try:
        experiment_info = experiment_service.get_experiment_by_id(data.experiment_id)
        if not experiment_info:
            raise HTTPException(status_code=404, detail="Experiment not found")
        
        experiment_date = experiment_info['Start_Datetime']
        gouge_area = calculate_gouge_area_from_blocks_dimensions(experiment_id=data.experiment_id)
        
        normal_stress_MPa = process_horizontal_load_measurements(
            experiment_id=data.experiment_id,
            machine_id=data.machine_id,
            experiment_date=experiment_date,
            gouge_area=gouge_area
        )
        
        return {"normal_stress_MPa": normal_stress_MPa.tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{experiment_id}/process_vertical_displacement", response_model=dict)
async def process_vertical_displacement(data: ExperimentReductionRequest):
    try:
        experiment_info = experiment_service.get_experiment_by_id(data.experiment_id)
        if not experiment_info:
            raise HTTPException(status_code=404, detail="Experiment not found")
        
        experiment_date = experiment_info['Start_Datetime']
        
        load_point_displacement_mm = process_load_point_displacement(
            experiment_id=data.experiment_id,
            machine_id=data.machine_id,
            experiment_date=experiment_date
        )
        
        return {"load_point_displacement_mm": load_point_displacement_mm.tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{experiment_id}/process_horizontal_displacement", response_model=dict)
async def process_horizontal_displacement(data: ExperimentReductionRequest):
    try:
        experiment_info = experiment_service.get_experiment_by_id(data.experiment_id)
        if not experiment_info:
            raise HTTPException(status_code=404, detail="Experiment not found")
        
        experiment_date = experiment_info['Start_Datetime']
        
        layer_thickness_mm = process_layer_thickness(
            experiment_id=data.experiment_id,
            machine_id=data.machine_id,
            experiment_date=experiment_date,
            layer_thickness_measured_mm=data.layer_thickness_measured_mm,
            layer_thickness_measured_point=data.layer_thickness_measured_point
        )
        
        return {"layer_thickness_mm": layer_thickness_mm.tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{experiment_id}/sync_ultrasonic_waveforms", response_model=dict)
async def sync_ultrasonic_waveforms(data: ExperimentReductionRequest):
    """
    Endpoint for synchronizing measurements to ultrasonic waveforms.
    """
    try:
        experiment_info = experiment_service.get_experiment_by_id(data.experiment_id)
        if not experiment_info:
            raise HTTPException(status_code=404, detail="Experiment not found")

        # Call the mock method from reduction_script
        result = synchronization_to_ultrasonic_waveforms(
            experiment_id=data.experiment_id,
            machine_id=data.machine_id
        )
        
        return {"synchronization_result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/find_blocks")
async def find_blocks():
    try:
        blocks = experiment_service.find_blocks()
        return blocks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add_block")
async def add_block(block: dict):
    try:
        success = experiment_service.add_block(block)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{experiment_id}/save_measurements")
async def save_measurements(experiment_id: str, measurements: List[Any]):
    try:
        file_location = f"/tmp/{experiment_id}_measurements.csv"
        with open(file_location, "w", newline='') as csvfile:
            fieldnames = ['id', 'experiment_id', 'data', 'unit']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for measurement in measurements:
                writer.writerow(measurement.dict())
        return {"file_location": file_location}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

