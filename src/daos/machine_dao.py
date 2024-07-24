# src/daos/machine_dao.py
from typing import Dict, Any
import os
from nptdms import TdmsFile
import matplotlib.pyplot as plt
from daos.base_dao import BaseDao

# MongoDB connection details
url = os.getenv("MONGO_URL") or "mongodb://localhost:27017/"
db_name = os.getenv("DB_NAME") or "EPS"
machines_collection_name = os.getenv("COLLECTION_MACHINES") or "Machines"

class MachineDao(BaseDao):
    def __init__(self):
        """Initialize the MachineDao class with a connection to the MongoDB database."""
        super().__init__()
        self.collection_name = machines_collection_name

    def create(self, machine_id: str, machine_type: str, pistons: Dict[str, Any]) -> str:
        """Create a new machine in the database"""
        machine = {
            "_id" : machine_id,
            "machine_type" : machine_type,
            "pistons": pistons
        }
        conn, collection = self._get_connection(self.collection_name)

        try:
            collection.insert_one(machine)
            print(f"Machine {machine_id} added to database.")
        except Exception as err:
            print(f"Error: '{err}'")
        finally:
            conn.close()

        return
