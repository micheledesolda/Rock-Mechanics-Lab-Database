# rock_mechanics_lab_database/daos/machine_dao.py

from typing import Dict, Any, List
import os
import numpy as np
from datetime import datetime

from rock_mechanics_lab_database.daos.base_dao import BaseDao


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
        """
        Create a new machine in the database.

        Args:
            machine_id (str): Unique identifier for the machine.
            machine_type (str): Type of the machine.
            pistons (Dict[str, Any]): Pistons data including calibration and stiffness.

        Returns:
            str: The machine ID.
        """
        machine = {
            "_id": machine_id,
            "machine_type": machine_type,
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

        return machine_id

    def find_machine_by_id(self, machine_id: str) -> Dict[str, Any]:
        """
        Retrieve machine details by machine ID.

        Args:
            machine_id (str): Unique identifier for the machine.

        Returns:
            Dict[str, Any]: Machine details.
        """
        conn, collection = self._get_connection(self.collection_name)
        try:
            return collection.find_one({"_id": machine_id})
        except Exception as err:
            print(f"Error: '{err}'")
            return None
        finally:
            conn.close()

    def update_machine(self, machine_id: str, update_fields: Dict[str, Any]) -> str:
        """
        Update machine details.

        Args:
            machine_id (str): Unique identifier for the machine.
            update_fields (Dict[str, Any]): Fields to update.

        Returns:
            str: The machine ID.
        """
        conn, collection = self._get_connection(self.collection_name)
        try:
            collection.update_one({"_id": machine_id}, {"$set": update_fields})
            print(f"Machine {machine_id} updated successfully.")
        except Exception as err:
            print(f"Error: '{err}'")
        finally:
            conn.close()
        return machine_id

    def delete_machine(self, machine_id: str) -> str:
        """
        Delete a machine from the database.

        Args:
            machine_id (str): Unique identifier for the machine.

        Returns:
            str: The machine ID.
        """
        conn, collection = self._get_connection(self.collection_name)
        try:
            collection.delete_one({"_id": machine_id})
            print(f"Machine {machine_id} deleted from database.")
        except Exception as err:
            print(f"Error: '{err}'")
        finally:
            conn.close()
        return machine_id

    def add_piston_calibration(self, machine_id: str, piston_name: str, calibration: Dict[str, Any], calibration_date: str) -> str:
        """
        Add calibration data for a specific piston.

        Args:
            machine_id (str): Unique identifier for the machine.
            piston_name (str): Name of the piston ('Vertical' or 'Horizontal').
            calibration (Dict[str, Any]): Calibration coefficients.
            calibration_date (str): Date of the calibration.

        Returns:
            str: The machine ID.
        """
        conn, collection = self._get_connection(self.collection_name)
        try:
            calibration_entry = {
                "date": calibration_date,
                "coefficients": calibration["coefficients"]
            }
            collection.update_one(
                {"_id": machine_id},
                {"$push": {f"pistons.{piston_name}.calibration": calibration_entry}}
            )
            print(f"Calibration added for piston {piston_name} in machine {machine_id}.")
            return machine_id
        except Exception as err:
            print(f"Error: '{err}'")
        finally:
            conn.close()

    def add_stiffness_calibration(self, machine_id: str, piston_name: str, stiffness: Dict[str, Any], stiffness_date: str) -> str:
        """
        Add stiffness calibration data for a specific piston.

        Args:
            machine_id (str): Unique identifier for the machine.
            piston_name (str): Name of the piston ('vertical' or 'horizontal').
            stiffness (Dict[str, Any]): Stiffness calibration coefficients.
            stiffness_date (str): Date of the stiffness calibration.

        Returns:
            str: The machine ID.
        """
        conn, collection = self._get_connection(self.collection_name)
        try:
            stiffness_entry = {
                "date": stiffness_date,
                "coefficients": stiffness["coefficients"]
            }
            collection.update_one(
                {"_id": machine_id},
                {"$push": {f"pistons.{piston_name}.stiffness": stiffness_entry}}
            )
            print(f"Stiffness calibration added for piston {piston_name} in machine {machine_id}.")
            return machine_id
        except Exception as err:
            print(f"Error: '{err}'")
        finally:
            conn.close()

    def _get_latest_calibration(self, calibrations: List[Dict[str, Any]], date: datetime) -> Dict[str, Any]:
        calibrations.sort(key=lambda x: datetime.strptime(x["date"], "%A, %B %d, %Y %I:%M:%S %p"))
        for calibration in calibrations:
            if datetime.strptime(calibration["date"], "%A, %B %d, %Y %I:%M:%S %p") >= date:
                return calibration
        return calibrations[-1]
    
    def apply_calibration(self, machine_id: str, piston_name: str, voltage: float, experiment_date: str) -> float:
        """
        Apply the stored calibration data to convert voltage to force.

        Args:
            machine_id (str): Unique identifier for the machine.
            piston_name (str): Name of the piston ('Vertical' or 'Horizontal').
            voltage (float): Voltage measurement (offsetted).
            experiment_date (str): Date of the experiment.

        Returns:
            float: Converted force (kN).
        """
        conn, collection = self._get_connection(self.collection_name)
        try:
            machine = collection.find_one({"_id": machine_id})
            experiment_datetime = datetime.strptime(experiment_date, "%A, %B %d, %Y %I:%M:%S %p")
            calibration = self._get_latest_calibration(machine["pistons"][piston_name]["calibration"], experiment_datetime)            
            coefficients = calibration["coefficients"]
            poly = np.poly1d(coefficients)
            force = poly(voltage)
            print(f"Applied calibration for piston {piston_name} in machine {machine_id}.")
            return force
        except Exception as err:
            print(f"Error: '{err}'")
            return None
        finally:
            conn.close()
    
    def apply_stiffness_correction(self, machine_id: str, piston_name: str, force: float, experiment_date: str) -> float:
        """
        Apply the stored stiffness calibration data to correct force measurements.

        Args:
            machine_id (str): Unique identifier for the machine.
            piston_name (str): Name of the piston ('Vertical' or 'Horizontal').
            force (float): Force measurement (kN).
            experiment_date (str): Date of the experiment.

        Returns:
            float: Corrected stiffness.
        """
        conn, collection = self._get_connection(self.collection_name)
        try:
            machine = collection.find_one({"_id": machine_id})
            experiment_datetime = datetime.strptime(experiment_date, "%A, %B %d, %Y %I:%M:%S %p")
            stiffness = self._get_latest_calibration(machine["pistons"][piston_name]["stiffness"], experiment_datetime)
            coefficients = stiffness["coefficients"]
            poly = np.poly1d(coefficients)
            corrected_stiffness = poly(force)
            print(f"Applied stiffness correction for piston {piston_name} in machine {machine_id}.")
            return corrected_stiffness
        except Exception as err:
            print(f"Error: '{err}'")
            return None
        finally:
            conn.close()
