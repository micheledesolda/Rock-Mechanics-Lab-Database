import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture(scope="module")
def test_client():
    return TestClient(app)

def test_create_block(test_client):
    response = test_client.post("/blocks/", json={
        "block_id": "block_001",
        "material": "steel",
        "dimensions": {"length": 10.0, "width": 5.0, "height": 2.0},
        "sensor_rail_width": 0.5,
        "sensors": []
    })
    assert response.status_code == 200
    assert response.json() == {"message": "Block created successfully"}


def test_get_block(test_client):
    response = test_client.get("/blocks/block_001")
    assert response.status_code == 200
    assert response.json()["material"] == "steel"

def test_create_core_sample(test_client):
    response = test_client.post("/core_samples/", json={
        "core_sample_id": "core_sample_001",
        "material": "granite",
        "dimensions": {"diameter": 10.0, "height": 20.0}
    })
    assert response.status_code == 200
    assert response.json() == {"message": "Core sample created successfully"}

def test_get_core_sample(test_client):
    response = test_client.get("/core_samples/core_sample_001")
    assert response.status_code == 200
    assert response.json()["material"] == "granite"

def test_create_gouge(test_client):
    response = test_client.post("/gouges/", json={
        "gouge_id": "gouge_001",
        "material": "minusil",
        "grain_size_mum": "5"
    })
    assert response.status_code == 200
    assert response.json() == {"message": "Gouge created successfully"}

def test_get_gouge(test_client):
    response = test_client.get("/gouges/gouge_001")
    assert response.status_code == 200
    assert response.json()["material"] == "minusil"


def test_create_sensor(test_client):
    response = test_client.post("/sensors/", json={
        "sensor_id": "PZT_1",
        "sensor_type": "piezoelectric",
        "resonance_frequency": 1.0,
        "dimensions" : {"side": 16, "height": 0.5, "units": "mm"},
        "properties": {"type": "factory", "date": "2023-01-01"},
    })
    assert response.status_code == 200
    assert response.json() == {"message": "Sensor created successfully"}

def test_get_sensor(test_client):
    response = test_client.get("/sensors/PZT_1")
    assert response.status_code == 200
    assert response.json()["model"] == "P-871.20"

def test_reduce_experiment(test_client):
    response = test_client.post("/experiments/reduce_experiment", json={
        "experiment_id": "s0150st05anh_30",
        "machine_id": "Brava2",
        "layer_thickness_measured_mm": 6,
        "layer_thickness_measured_point": 0
    })
    assert response.status_code == 200
    data = response.json()
    assert "shear_stress_MPa" in data
    assert "normal_stress_MPa" in data
    assert "load_point_displacement_mm" in data
    assert "layer_thickness_mm" in data
    assert isinstance(data["shear_stress_MPa"], list)
    assert isinstance(data["normal_stress_MPa"], list)
    assert isinstance(data["load_point_displacement_mm"], list)
    assert isinstance(data["layer_thickness_mm"], list)
