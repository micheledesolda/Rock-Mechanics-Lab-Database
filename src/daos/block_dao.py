# src/daos/block_dao.py
import pymongo
from typing import List, Dict, Optional, Union, Tuple, Any
import os
import sys
import csv
import json
import gridfs
from nptdms import TdmsFile
import matplotlib.pyplot as plt
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

    def create(self, block_id: str, material: str, dimensions: Dict[str, float], sensor_rail_width: float, sensors: List[Dict] = []) -> None:
        """Create a new block in the database."""
        conn, collection = self._get_connection(self.collection_name)
        block = {
            "_id": block_id,
            "material": material,
            "dimensions": dimensions,
            "sensor_rail_width": sensor_rail_width,
            "sensors": sensors
        }
        try:
            collection.insert_one(block)
            print(f"Block {block_id} added to database.")
        except Exception as err:
            print(f"Error: '{err}'")
        finally:
            conn.close()

    def add_sensor(self, block_id: str, sensor_id: str,sensor_name: str, position: Dict[str, float], orientation:str, calibration: str) -> None:
        """Add a sensor to a block."""
        conn, collection = self._get_connection(self.collection_name)
        sensorDao = SensorDao()
        sensor = sensorDao.find_sensor_by_id(sensor_id)
        
        if sensor is None:
            print(f"Sensor with ID {sensor_id} not found.")
            conn.close()
            return
        
        sensor_entry = {
            "_id": sensor_name,
            "position": position,
            "orientation": orientation,
            "calibration": calibration,
            "sensor_properties": sensor
        }
        
        try:
            collection.update_one({"_id": block_id}, {"$push": {"sensors": sensor_entry}})
            print(f"Sensor {sensor_name} added to block {block_id}.")
        except Exception as err:
            print(f"Error: '{err}'")
        finally:
            conn.close()

    def find_block_by_id(self, _id: str) -> Optional[Dict]:
        """Retrieve sensor details by sensor ID."""
        conn, collection = self._get_connection(self.collection_name)
        try:
            sensor = collection.find_one({"_id": _id})
            return sensor
        except Exception as err:
            print(f"Error: '{err}'")
            return None
        finally:
            conn.close() 
