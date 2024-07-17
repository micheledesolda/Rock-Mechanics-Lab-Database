# tests/test_block_api.py

import pytest
from fastapi.testclient import TestClient
from mongoengine import connect, disconnect, get_connection
import mongomock

from main import app

client = TestClient(app)

@pytest.fixture(scope='module')
def mongo():
    connection = connect('mongoenginetest', host='mongodb://localhost', mongo_client_class=mongomock.MongoClient)
    yield connection
    disconnect()

def test_create_block(mongo):
    block_data = {
        "block_id": "block1",
        "material": "steel",
        "dimensions": {"length": 100.0, "width": 50.0, "height": 25.0},
        "sensor_rail_width": 10.0,
        "sensors": []
    }
    response = client.post("/blocks", json=block_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Block created successfully"}

def test_get_block(mongo):
    block_id = "block1"
    response = client.get(f"/blocks/{block_id}")
    assert response.status_code == 200
    block = response.json()
    assert block["block_id"] == block_id
    assert block["material"] == "steel"
    assert block["dimensions"] == {"length": 100.0, "width": 50.0, "height": 25.0}