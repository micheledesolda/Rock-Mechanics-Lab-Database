# src/daos/block_dao.py
from typing import List, Dict, Optional, Union, Tuple, Any
import os
from daos.base_dao import BaseDao
from daos.sensor_dao import SensorDao

# MongoDB connection details
url = os.getenv("MONGO_URL") or "mongodb://localhost:27017/"
db_name = os.getenv("DB_NAME") or "EPS"
blocks_collection_name = os.getenv("COLLECTION_BLOCKS") or "Blocks"


class BlockDao(BaseDao):
    def __init__(self):
        """Initialize the BlockDao class with a connection to the MongoDB database."""
        super().__init__()
        self.collection_name = blocks_collection_name


    def create(self, 
            block_id: str, 
            material: str, 
            velocities: Dict[str, Any],
            dimensions: Dict[str, float],
            sensor_rail_width: float, 
            sensors: List[Dict] = [],
            description: str = "") -> None:
        """Create a new block in the database."""
        conn, collection = self._get_connection(self.collection_name)

        block = {
            "_id":block_id,
            "material":material,
            "velocities": velocities,
            "dimensions":dimensions,
            "sensor_rail_width":sensor_rail_width,
            "sensors":[],
            "description" : description
        }

        try:
            collection.insert_one(block)
            for sensor in sensors:
                self.add_sensor(block_id=block["_id"], 
                                sensor_id=sensor["sensor_id"], 
                                sensor_name=sensor["sensor_name"],
                                position=sensor["position"],
                                orientation=sensor["orientation"])
            print(f"Block {block_id} added to database.")
        except Exception as err:
            print(f"Error: '{err}'")
        finally:
            conn.close()

    def add_sensor(self, block_id: str, 
                   sensor_id: str, 
                   sensor_name: str, 
                   position: Dict[str, float], 
                   orientation: str, 
                   calibration: str) -> None:
        """Add a sensor to a block."""
        conn, collection = self._get_connection(self.collection_name) 
        sensorDao = SensorDao()
        sensor = sensorDao.find_sensor_by_id(sensor_id=sensor_id)
        if sensor is None:
            return f"Sensor with ID {sensor_id} not found."

        sensor_entry = {"_id": sensor_id, 
                        "sensor_name" : sensor_name,
                        "position": position,
                        "orientation": orientation,
                        "calibration": calibration}
        try:
            update_result = collection.update_one(
                {"_id": block_id},
                {"$push": {"sensors": sensor_entry}}
            )
            return f"Sensor {sensor_name} added to block {block_id}." if update_result.modified_count > 0 else f"Failed to add sensor {sensor_id} to block {block_id}."

        except Exception as err:
            print(f"Error: '{err}'")
        finally:
            conn.close() 

    def find_block_by_id(self, block_id: str) -> Optional[Dict]:
        """Retrieve block details by sensor ID."""
        conn, collection = self._get_connection(self.collection_name)
        try:
            block = collection.find_one({"_id": block_id})
            s = f"block {block_id} found"
            print(s)
            return block
        except Exception as err:
            print(f"block {block_id} not found\nError: '{err}'")
            return None
        finally:
            conn.close()   

    def get_sensor_properties(self, sensor_id: str) -> Dict:
        # Implementation for retrieving sensor properties
        pass

