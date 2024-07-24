# tests/test_services.py
import pytest
from services.block_service import BlockService
from services.core_sample_service import CoreSampleService
from services.experiment_service import ExperimentService
from services.gouge_service import GougeService
from services.machine_service import MachineService
from services.sensor_service import SensorService

@pytest.fixture
def block_service():
    return BlockService()

@pytest.fixture
def core_sample_service():
    return CoreSampleService()

@pytest.fixture
def experiment_service():
    return ExperimentService()

@pytest.fixture
def gouge_service():
    return GougeService()

@pytest.fixture
def machine_service():
    return MachineService()

@pytest.fixture
def sensor_service():
    return SensorService()

def test_create_block(block_service):
    block_id = "block_001"
    material = "steel"
    dimensions = {"length": 10.0, "width": 5.0, "height": 2.0}
    sensor_rail_width = 0.5
    sensors = []
    result = block_service.create_block(block_id, material, dimensions, sensor_rail_width, sensors)
    assert result == block_id

def test_create_core_sample(core_sample_service):
    core_sample_id = "core_sample_001"
    material = "granite"
    dimensions = {"diameter": 10.0, "height": 20.0}
    result = core_sample_service.create_core_sample(core_sample_id, material, dimensions)
    assert result == core_sample_id

def test_create_experiment(experiment_service):
    experiment_id = "experiment_001"
    experiment_type = "type_001"
    gouges = []
    core_sample_id = "core_sample_001"
    blocks = []
    centralized_measurements = []
    additional_measurements = []
    result = experiment_service.create_experiment(experiment_id, experiment_type, gouges, core_sample_id, blocks, centralized_measurements, additional_measurements)
    assert result == experiment_id

def test_create_gouge(gouge_service):
    gouge_id = "gouge_001"
    thickness_mm = "10"
    grain_size_mum = "5"
    result = gouge_service.create_gouge(gouge_id, thickness_mm, grain_size_mum)
    assert result == gouge_id

def test_create_machine(machine_service):
    machine_id = "Brava2"
    properties = {}
    pistons = "2"
    result = machine_service.create_machine(machine_id, properties, pistons)
    assert result == machine_id


def test_create_sensor(sensor_service):
    sensor_id = "sensor_001"
    model = "model_001"
    resonance_frequency = 2.5
    calibration = {"type": "factory", "date": "2023-01-01"}
    properties = {"location": "lab", "status": "active"}
    result = sensor_service.create_sensor(sensor_id, model, resonance_frequency, calibration, properties)
    assert result == sensor_id



