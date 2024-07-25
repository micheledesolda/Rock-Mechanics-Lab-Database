# src/tests/test_experiment_services.py

import pytest
import os
from services.experiment_service import ExperimentService

DIRNAME = os.path.dirname(__file__)
TEST_DIR = os.path.join(DIRNAME, '../tests/test_data')
FILE_NAME = "s0074sa03min50.tdms"
FILE_NAME1 = "s0108sw06car102030.tdms"
EXPERIMENT_ID = FILE_NAME.split(".")[0]
EXPERIMENT_ID1 = FILE_NAME1.split(".")[0]
EXPERIMENT_PATH = os.path.join(TEST_DIR,FILE_NAME)
EXPERIMENT_PATH1 = os.path.join(TEST_DIR,FILE_NAME1)
UW_NAME = "001_run_in_10MPa.bscan.tsv"
UW_PATH = os.path.join(TEST_DIR,UW_NAME)

@pytest.fixture(scope="module")
def experiment_service():
    return ExperimentService()

def test_create_experiment_from_scratch(experiment_service):
    experiment_id = "experiment_001"
    experiment_type = "Double Direct Shear"
    gouges = [{"gouge_id": "gouge_001", "thickness_mm": "10"}]
    core_sample_id = "core_sample_001"
    blocks = [{"block_id": "block_001", "position": "left"}]
    centralized_measurements = []
    additional_measurements = []

    result = experiment_service.create_experiment(experiment_id, experiment_type, gouges, core_sample_id, blocks, centralized_measurements, additional_measurements)
    assert result == experiment_id

def test_create_experiment(experiment_service):
    experiment_id = EXPERIMENT_ID
    experiment_type = "Unknown"
    gouges = [{"gouge_id": "gouge_001", "thickness_mm": "10"}]
    blocks = [{"block_id": "block_001", "position": "left"}]
    centralized_measurements = []
    additional_measurements = []

    result = experiment_service.create_experiment(experiment_id, experiment_type, gouges, blocks, centralized_measurements, additional_measurements)
    assert result == experiment_id

def test_create_experiment_from_file(experiment_service):
    file_path = EXPERIMENT_PATH1
    gouges = [{"gouge_id": "gouge_001", "thickness_mm": "10"}]
    blocks = [{"block_id": "block_001", "position": "left"}]

    result = experiment_service.create_experiment_from_file(file_path, gouges, blocks)
    assert result == EXPERIMENT_ID1

def test_get_experiment_by_id(experiment_service):
    experiment_id = EXPERIMENT_ID
    result = experiment_service.get_experiment_by_id(experiment_id)
    assert result["_id"] == experiment_id

def test_update_experiment(experiment_service):
    experiment_id = EXPERIMENT_ID1
    update_fields = {"experiment_type": "Double Direct Shear"}
    result = experiment_service.update_experiment(experiment_id, update_fields)
    assert result == experiment_id

def test_add_block(experiment_service):
    experiment_id = EXPERIMENT_ID
    block_id = "block_002"
    position = "right"
    result = experiment_service.add_block(experiment_id, block_id, position)
    assert result == block_id

def test_add_gouge(experiment_service):
    experiment_id = EXPERIMENT_ID1
    gouge_id = "gouge_002"
    thickness_mm = "15"
    result = experiment_service.add_gouge(experiment_id, gouge_id, thickness_mm)
    assert result == gouge_id

def test_add_centralized_measurements_from_tdms_file(experiment_service):
    experiment_id = EXPERIMENT_ID
    file_path = EXPERIMENT_PATH
    result = experiment_service.add_centralized_measurements_from_tdms_file(experiment_id, file_path)
    assert isinstance(result, dict)

def test_add_ultrasonic_waveforms_from_tsv_file(experiment_service):
    experiment_id = EXPERIMENT_ID1
    file_path = UW_PATH
    result = experiment_service.add_ultrasonic_waveforms_from_tsv_file(experiment_id, file_path)
    assert isinstance(result, dict)

def test_delete_experiment(experiment_service):
    experiment_id = "experiment_001"
    result = experiment_service.delete_experiment(experiment_id)
    assert result == f"Experiment {experiment_id} deleted from database"
