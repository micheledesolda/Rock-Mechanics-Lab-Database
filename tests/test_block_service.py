# tests/test_block_service.py
import pytest
from services.block_service import BlockService
from mongoengine import connect, disconnect

@pytest.fixture(scope='module')
def mongo():
    connect('mongoenginetest', host='mongomock://localhost')
    yield
    disconnect()

@pytest.fixture
def block_service(mongo):
    return BlockService()

def test_create_block(block_service):
    block_data = {
        "block_id": "block1",
        "material": "steel",
        "dimensions": {"length": 100.0, "width": 50.0, "height": 25.0},
        "sensor_rail_width": 10.0,
        "sensors": []
    }
    result = block_service.create_block(block_data)
    assert result is None  # create() method doesn't return anything
