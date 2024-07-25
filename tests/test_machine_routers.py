# tests/test_machine_routers.py

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture(scope="module")
def test_client():
    return TestClient(app)

def test_create_machine(test_client):
    response = test_client.post("/machines/", json={
        "machine_id": "Brava2",
        "machine_type": "Biaxial Apparatus",
        "pistons": {
            "vertical": {
                "calibration": [{"date": "Wednesday, March 15, 2023 9:52:34 AM", "coefficients": [-0.5043737 , 4.27584024, -11.70546934, 5.45745069,
                                           29.43390033, -60.90428874, 60.98729795, 124.19783947,
                                           -0.47000267]}],
                "stiffness": [{"date": "Wednesday, March 15, 2023 9:52:34 AM", "coefficients": [2.43021220e-31, -7.73507440e-28, 1.10791696e-24, -9.43050473e-22,
                                           5.30556343e-19, -2.07533887e-16, 5.77817817e-14, -1.15148744e-11,
                                           1.62528123e-09, -1.57483543e-07, 9.75756659e-06, -3.16390679e-04,
                                           1.96801181e-04, 2.69515293e-01, 5.53939566e+00, 4.21560673e+01]}]
            },
            "horizontal": {
                "calibration": [{"date": "Wednesday, March 15, 2023 9:52:34 AM", "coefficients": [-4.63355231e-02, -2.57055418e+00, 2.63055688e+01, -9.61932787e+01,
                                           1.64685122e+02, -1.33648859e+02, 4.66773182e+01, 1.63975941e+02,
                                           9.32438525e-02]}],
                "stiffness": [{"date": "Wednesday, March 15, 2023 9:52:34 AM", "coefficients": [2.43021220e-31, -7.73507440e-28, 1.10791696e-24, -9.43050473e-22,
                                           5.30556343e-19, -2.07533887e-16, 5.77817817e-14, -1.15148744e-11,
                                           1.62528123e-09, -1.57483543e-07, 9.75756659e-06, -3.16390679e-04,
                                           1.96801181e-04, 2.69515293e-01, 5.53939566e+00, 4.21560673e+01]}]
            }
        }
    })
    assert response.status_code == 200
    assert response.json() == {"message": "Machine created successfully"}

def test_get_machine(test_client):
    response = test_client.get("/machines/Brava2")
    assert response.status_code == 200
    assert response.json()["machine_type"] == "Biaxial Apparatus"

def test_add_piston_calibration(test_client):
    response = test_client.post("/machines/Brava2/calibration", json={
        "piston_name": "vertical",
        "calibration": {"coefficients": [-0.5043737 , 4.27584024, -11.70546934, 5.45745069,
                                         29.43390033, -60.90428874, 60.98729795, 124.19783947,
                                         -0.47000267]},
        "calibration_date": "Thursday, March 16, 2023 10:00:00 AM"
    })
    assert response.status_code == 200
    assert response.json() == {"message": "Piston calibration added successfully"}

def test_add_stiffness_calibration(test_client):
    response = test_client.post("/machines/Brava2/stiffness", json={
        "piston_name": "horizontal",
        "stiffness": {"coefficients": [2.43021220e-31, -7.73507440e-28, 1.10791696e-24, -9.43050473e-22,
                                       5.30556343e-19, -2.07533887e-16, 5.77817817e-14, -1.15148744e-11,
                                       1.62528123e-09, -1.57483543e-07, 9.75756659e-06, -3.16390679e-04,
                                       1.96801181e-04, 2.69515293e-01, 5.53939566e+00, 4.21560673e+01]},
        "stiffness_date": "Thursday, March 16, 2023 10:00:00 AM"
    })
    assert response.status_code == 200
    assert response.json() == {"message": "Stiffness calibration added successfully"}

def test_apply_calibration(test_client):
    response = test_client.post("/machines/Brava2/apply_calibration", json={
        "piston_name": "horizontal",
        "voltage": 0.5,
        "experiment_id": "s0108"
    })
    assert response.status_code == 200
    assert "result" in response.json()

def test_apply_stiffness_correction(test_client):
    response = test_client.post("/machines/Brava2/apply_stiffness", json={
        "piston_name": "vertical",
        "force": 100.0,
        "experiment_id": "s0108"
    })
    assert response.status_code == 200
    assert "result" in response.json()
