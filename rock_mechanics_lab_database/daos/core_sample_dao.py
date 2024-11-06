# rock_mechanics_lab_database/daos/core_sample_dao.py
import pymongo
from typing import List, Dict, Optional, Union, Tuple, Any
import os
import sys
import csv
import json
import gridfs
from nptdms import TdmsFile
import matplotlib.pyplot as plt
from rock_mechanics_lab_database.daos.base_dao import BaseDao

# MongoDB connection details
url = os.getenv("MONGO_URL") or "mongodb://localhost:27017/"
db_name = os.getenv("DB_NAME") or "EPS"
coresamples_collection_name = os.getenv("COLLECTION_CORESAMPLES") or "CoreSamples"

class CoreSampleDao(BaseDao):
    def __init__(self):
        """Initialize the CoreSampleDao class with a connection to the MongoDB database."""
        super().__init__()
        self.collection_name = coresamples_collection_name

    def create(self, core_sample_id: str, material: str, dimensions: Dict[str, float], sensors: List[str] = []) -> None:

        """Create a new core sample in the database."""
        core_sample = {
            "_id": core_sample_id,
            "material": material,
            "dimensions": dimensions,
            "sensors": sensors
        }
        conn, collection = self._get_connection(self.collection_name)

        try:
            collection.insert_one(core_sample)
            print(f"Core sample {core_sample_id} added to database.")
        except Exception as err:
            print(f"Error: '{err}'")
        finally:
            conn.close()
    
    def update_sensors(self, core_sample_id: str, _id: str) -> None:
        """Update sensors for a given core sample."""
        conn, collection = self._get_connection(self.collection_name)

        try:
            collection.update_one({"_id": core_sample_id}, {"$push": {"sensors": _id}})
            print(f"Sensor {_id} added to core sample {core_sample_id}.")
        except Exception as err:
            print(f"Error: '{err}'")
        finally:
            conn.close()
