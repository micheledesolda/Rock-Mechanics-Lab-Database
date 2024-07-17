# tests/test_block_service.py

import pytest
from mongoengine import connect, disconnect
import mongomock
from services.block_service import BlockService

@pytest.fixture(scope='module')
def mongo():
    connection = connect('mongoenginetest', host='mongodb://localhost', mongo_client_class=mongomock.MongoClient)
    yield connection
    disconnect()

def test_create_block_service(mongo):
    block_service = BlockService()
    block_data = {
        "block_id": "block1",
        "material": "steel",
        "dimensions": {"length": 100.0, "width": 50.0, "height": 25.0},
        "sensor_rail_width": 10.0,
        "sensors": []
    }
    result = block_service.create_block(block_data)
    assert result == {"message": "Block created successfully"}

# Add more tests as needed
