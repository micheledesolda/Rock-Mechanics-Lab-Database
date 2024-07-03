# src/daos/block_dao.py
import pymongo
from typing import List, Dict, Optional, Union, Tuple, Any
import os
from mongoengine import connect, DoesNotExist
from models.models import Block, Sensor

# MongoDB connection details
url = os.getenv("MONGO_URL") or "mongodb://localhost:27017/"
db_name = os.getenv("DB_NAME") or "EPS"
blocks_collection_name = os.getenv("COLLECTION_BLOCKS") or "Blocks"


class BlockDao:
    def __init__(self):
        """Initialize the BlockDao class with a connection to the MongoDB database."""
        self.db = connect(db_name, host=url)

    def create(self, block_id: str, material: str, dimensions: Dict[str, float], sensor_rail_width: float, sensors: List[Dict] = []) -> None:
        """Create a new block in the database."""
        block = Block(
            block_id=block_id,
            material=material,
            dimensions=dimensions,
            sensor_rail_width=sensor_rail_width,
            sensors=[Sensor(**sensor) for sensor in sensors]
        )
        try:
            block.save()
            print(f"Block {block_id} added to database.")
        except Exception as err:
            print(f"Error: '{err}'")

    def add_sensor(self, block_id: str, sensor_id: str, sensor_name: str, position: Dict[str, float], orientation: str, calibration: str) -> None:
        """Add a sensor to a block."""
        try:
            block = Block.objects.get(block_id=block_id)
            sensor = Sensor(
                sensor_name=sensor_name,
                position=position,
                orientation=orientation,
                calibration=calibration,
                sensor_properties=self.get_sensor_properties(sensor_id)
            )
            block.sensors.append(sensor)
            block.save()
            print(f"Sensor {sensor_name} added to block {block_id}.")
        except DoesNotExist:
            print(f"Block with ID {block_id} not found.")
        except Exception as err:
            print(f"Error: '{err}'")

    def find_block_by_id(self, block_id: str) -> Optional[Dict]:
        """Retrieve block details by block ID."""
        try:
            block = Block.objects.get(block_id=block_id)
            return block.to_mongo().to_dict()
        except DoesNotExist:
            print(f"Block with ID {block_id} not found.")
            return None
        except Exception as err:
            print(f"Error: '{err}'")
            return None

    def get_sensor_properties(self, sensor_id: str) -> Dict:
        # Implementation for retrieving sensor properties
        pass

