# rock_mechanics_lab_database/daos/gouge_dao.py
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

# MongoDB connection details
url = os.getenv("MONGO_URL") or "mongodb://localhost:27017/"
db_name = os.getenv("DB_NAME") or "EPS"
gouges_collection_name = os.getenv("COLLECTION_GOUGES") or "Gouges"

class GougeDao(BaseDao):
    def __init__(self):
        """Initialize the GougeDao class with a connection to the MongoDB database."""
        super().__init__()
        self.collection_name = gouges_collection_name

    def create(self, gouge_id: str, material: str, grain_size: float) -> None:
        """Create a new gouge in the database."""
        conn, collection = self._get_connection(self.collection_name)

        gouge = {
            "_id": gouge_id,
            "material": material,
            "grain_size": grain_size
        }
        try:
            collection.insert_one(gouge)
            print(f"Gouge {gouge_id} added to database.")
        except Exception as err:
            print(f"Error: '{err}'")
        finally:
            conn.close()

    def find_gouge_by_id(self, _id: str) -> Optional[Dict]:
        """Retrieve sensor details by sensor ID."""
        conn, collection = self._get_connection(self.collection_name)

        try:
            gouge = collection.find_one({"_id": _id})
            return gouge
        except Exception as err:
            print(f"Error: '{err}'")
            return None
        finally:
            conn.close()
