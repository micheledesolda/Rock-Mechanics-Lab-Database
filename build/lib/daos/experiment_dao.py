from typing import List, Dict, Optional, Union
import os
import json
import gridfs
from nptdms import TdmsFile
from daos.base_dao import BaseDao
from daos.block_dao import BlockDao
from daos.gouge_dao import GougeDao

# Constants
MAXIMUM_SIZE = 16000000
CHUNK_SIZE = int(MAXIMUM_SIZE / 64)
experiments_collection_name = os.getenv("COLLECTION_EXPERIMENTS") or "Experiments"

class ExperimentDao(BaseDao):
    def __init__(self):
        """Initialize the ExperimentDao class with a connection to the MongoDB database."""
        super().__init__()
        self.collection_name = experiments_collection_name
        conn, _ = self._get_connection(self.collection_name)
        db = conn[self.db_name]
        self.fs = gridfs.GridFS(db)

### CRUD logic implementation ###
### Create: exposed method
    def create_experiment(self, experiment_id: str = "", experiment_type: str = "", gouges: List[dict] = [], 
                          core_sample_id: Optional[str] = None, blocks: List[Dict] = [], 
                          centralized_measurements: List[Dict] = [], additional_measurements: List[Dict] = []) -> str:
        """Create a new experiment in the database."""
        experiment = self._initialize_experiment(
            experiment_id, experiment_type, core_sample_id, blocks, centralized_measurements, additional_measurements
        )
        return self._insert_experiment_and_add_elements(experiment, blocks, gouges)

    def create_experiment_from_file(self, file_path: str, gouges: List[dict] = [], blocks: List[Dict] = []) -> str:
        """Create a new experiment from a file."""
        if not os.path.isfile(file_path):
            raise ValueError(f"File path {file_path} is not a valid file path")

        experiment_id = os.path.basename(file_path).split(".")[0]
        tdms_dict = self._read_experiment_tdms_file(file_path=file_path)

        experiment = self._initialize_experiment(
            experiment_id, tdms_dict.get("experiment_type", ""), None, blocks, [], []
        )
        experiment.update(tdms_dict["properties"])

        try:
            self._insert_experiment_and_add_elements(experiment, blocks, gouges)
            self._add_centralized_measurements_from_tdms_dictionary(experiment_id=experiment["_id"], tdms_dict=tdms_dict)
            return experiment["_id"]
        except Exception as err:
            print(f"Adding experiment from file {file_path} failed!\nError: '{err}'")
            return ""

### Create: helper methods
    def _initialize_experiment(self, experiment_id: str, experiment_type: str, core_sample_id: Optional[str], 
                               blocks: List[Dict], centralized_measurements: List[Dict], additional_measurements: List[Dict]) -> Dict:
        """Initialize the experiment dictionary."""
        return {
            "_id": experiment_id,
            "experiment_type": experiment_type,
            "gouges": [],
            "core_sample_id": core_sample_id,
            "blocks": [],
            "centralized_measurements": centralized_measurements,
            "additional_measurements": additional_measurements
        }

    def _insert_experiment_and_add_elements(self, experiment: Dict, blocks: List[Dict], gouges: List[Dict], conn=None) -> str:
        """Insert the experiment into the database and add blocks and gouges."""
        if not conn:
            conn, collection = self._get_connection(self.collection_name)
        else:
            collection = conn[self.collection_name]

        try:
            collection.insert_one(experiment)
            for block in blocks:
                self.add_block(experiment_id=experiment["_id"], block_id=block['block_id'], position=block['position'])
            for gouge in gouges:
                self.add_gouge(experiment_id=experiment["_id"], gouge_id=gouge["gouge_id"], thickness_mm=gouge["thickness_mm"])
            return experiment["_id"]
        except Exception as err:
            print(f"Adding experiment {experiment['_id']} to database failed!\nError: '{err}'")
            return ""
        finally:
            if not conn:
                conn.close()

### READ
### Read: exposed methods
    def read(self, offset: int, limit: int) -> Union[List[Dict], str]:
        """Read experiments from the database with pagination."""
        try:
            conn, collection = self._get_connection(self.collection_name)
            experiments = collection.find().skip((offset - 1) * limit).limit(limit)
            experiment_list = [{'_id': str(experiment['_id']), **experiment} for experiment in experiments]            
            return experiment_list if experiment_list else "No experiments found"

        except Exception as err:
            return f"Something went wrong reading experiments from database:\nError: '{err}'"
        finally:
            conn.close()

    def find_experiment_by_id(self, experiment_id: str) -> Optional[Dict]:
        """Retrieve experiment details by ID."""
        conn, collection = self._get_connection(self.collection_name)
        try:
            experiment = collection.find_one({"_id": experiment_id})
            if experiment:
                print(f"Experiment {experiment_id} found")
            else:
                print(f"Experiment {experiment_id} not found")
            return experiment
        except Exception as err:
            print(f"Error retrieving experiment {experiment_id}:\nError: '{err}'")
            return None
        finally:
            conn.close()

    def find_centralized_measurements(self, experiment_id: str, group_name: str, channel_name: str) -> Dict:
        """Retrieve centralized measurements and properties for a specific experiment and channel."""
        measurement = self._get_measurement_properties(experiment_id, group_name, channel_name)
        if not measurement:
            return {}
        
        properties = measurement.get("properties", {})
        data = self._get_measurement_data(measurement)
        
        return {"properties": properties, "data": data}

### Read: helper methods
    def _get_measurement_data(self, measurement: Dict) -> List:
        """Retrieve data from measurement, either from GridFS or directly."""
        data = []
        try:
            # Data is stored in chunks
            file_ids = measurement.get("data", [])
            for file_id in file_ids:
                chunk = json.loads(self.fs.get(file_id).read())
                data.extend(chunk)
        except Exception as err:
            print(f"Error retrieving measurement data:\nError: '{err}'")
        return data

    def _get_measurement_properties(self, experiment_id: str, group_name: str, channel_name: str) -> Dict:
        """Retrieve properties of the specified measurement."""
        conn, collection = self._get_connection(self.collection_name)
        try:
            measurement = collection.find_one(
                {"_id": experiment_id},
                {f"centralized_measurements.{group_name}.{channel_name}": 1, "_id": 0}
            )["centralized_measurements"][group_name][channel_name]
            return measurement
        except Exception as err:
            print(f"Error retrieving measurement properties:\nError: '{err}'")
            return {}
        finally:
            conn.close()

### UPDATE
# Update: exposed methods
    def update(self, experiment_id: str, update_fields: Dict) -> str:
        """Update an experiment in the database."""
        conn, collection = self._get_connection(self.collection_name) 
        try:
            update_result = collection.update_one({"_id": experiment_id}, {"$set": update_fields})
            return f"Experiment {experiment_id} updated successfully" if update_result.modified_count > 0 else f"No changes made to experiment {experiment_id}"
        except Exception as err:
            return f"Error updating experiment {experiment_id}:\nError: '{err}'"
        finally:
            conn.close()

    def add_block(self, experiment_id: str, block_id: str, position: str) -> str:
        """Add a block to an experiment."""
        blockDao = BlockDao()
        block = blockDao.find_block_by_id(block_id)
        if not block:
            return f"Block with ID {block_id} not found."

        block_entry = {"_id": block_id, "position": position}
        try:
            update_result = self.update(
                experiment_id,
                {"$push": {"blocks": block_entry}}
            )
            return f"Block {block_id} added to experiment {experiment_id} at position {position}." if "updated successfully" in update_result else f"Failed to add block {block_id} to experiment {experiment_id}."
        except Exception as err:
            return f"Error adding block to experiment:\nError: '{err}'"

    def add_gouge(self, experiment_id: str, gouge_id: str, thickness_mm: str) -> str:
        """Add a gouge to an experiment."""
        gougeDao = GougeDao()
        gouge = gougeDao.find_gouge_by_id(gouge_id)
        if not gouge:
            return f"Gouge with ID {gouge_id} not found."

        gouge_entry = {"_id": gouge_id, "thickness_mm": thickness_mm}
        try:
            update_result = self.update(
                experiment_id,
                {"$push": {"gouges": gouge_entry}}
            )
            return f"Gouge {gouge_id} added to experiment {experiment_id}." if "updated successfully" in update_result else f"Failed to add gouge {gouge_id} to experiment {experiment_id}."
        except Exception as err:
            return f"Error adding gouge to experiment:\nError: '{err}'"

    def add_centralized_measurements_from_tdms_file(self, experiment_id: str, file_path: str) -> Dict:
        """Store large TDMS measurement data in GridFS and update the experiment document."""
        conn, _ = self._get_connection(self.collection_name)

        try:
            tdms_dict = self._read_experiment_tdms_file(file_path=file_path)
            self._add_centralized_measurements_from_tdms_dictionary(experiment_id=experiment_id, tdms_dict=tdms_dict)
            print(f"Added measurements from tdms file {file_path} to experiment {experiment_id}")
            return tdms_dict
        except Exception as err:
            print(f"Failed to add measurements from tdms file {file_path} to experiment {experiment_id}:\nError: '{err}'")
            return {}
        finally:
            conn.close()

### Update: helper methods
    def _add_centralized_measurements_from_tdms_dictionary(self, experiment_id: str, tdms_dict: Dict) -> Dict:
        """Extract and store centralized measurements from a TDMS dictionary in GridFS and update the experiment document."""
        conn, _ = self._get_connection(self.collection_name)
        try:
            data_chunk = {}
            for group_name, group_data in tdms_dict['groups'].items():
                for channel_name, channel_data in group_data['channels'].items():
                    data = channel_data['data']
                    properties = channel_data['properties']

                    if len(data) > CHUNK_SIZE:
                        key = f"{group_name}/{channel_name}/data"
                        file_ids = self._store_measurement_chunks(experiment_id, key=key, values=data, chunk_size=CHUNK_SIZE)
                        data_chunk.setdefault(group_name, {})[channel_name] = {
                            "properties": properties,
                            "data": file_ids
                        }
                    else:
                        data_chunk.setdefault(group_name, {})[channel_name] = {
                            "properties": properties,
                            "data": data
                        }

            update_result = self.update(experiment_id=experiment_id, update_fields={"centralized_measurements": data_chunk})
            print(f"Update result: {update_result}")
            return update_result
        except Exception as err:
            print(f"Failed to add centralized measurements to experiment {experiment_id}:\nError: '{err}'")
            return {}
        finally:
            conn.close()

    def _read_experiment_tdms_file(self, file_path: str) -> Dict[str, List[float]]:
        """Read and parse the measurement file into time series format."""
        try:
            tdms_file = TdmsFile.read(file_path)
            tdms_dict = {
                'properties': tdms_file.properties,
                'groups': {
                    group.name: {
                        'channels': {
                            channel.name: {
                                'properties': channel.properties,
                                'data': channel.data.tolist()
                            }
                            for channel in group.channels()
                        }
                    }
                    for group in tdms_file.groups()
                }
            }
            return tdms_dict
        except Exception as err:
            print(f"Error reading file {file_path}:\nError: '{err}'")
            return {}

### DELETE
### Delete: exposed methods
    def delete(self, experiment_id: str) -> str:
        """Delete an experiment from the database."""
        conn, collection = self._get_connection(self.collection_name)
        try:
            delete_result = collection.delete_one({"_id": experiment_id})
            return f"Experiment {experiment_id} deleted from database" if delete_result.deleted_count > 0 else f"Experiment {experiment_id} not found"
        except Exception as err:
            return f"Error deleting experiment {experiment_id}:\nError: '{err}'"
        finally:
            conn.close()

### Utils
    def _split_list(self, data: List[float], chunk_size: int) -> List[List[float]]:
        """Split a large list of floats into chunks of specified size."""
        return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    def _store_measurement_chunks(self, experiment_id: str, key: str, values: List, chunk_size: int) -> List[str]:
        """Store chunks of measurement data in GridFS and return the file IDs."""
        chunks = self._split_list(values, chunk_size)
        file_ids = []
        for index, chunk in enumerate(chunks):
            file_id = f"{experiment_id}_{key}_{index}"
            self.fs.put(json.dumps(chunk).encode('utf-8'), _id=file_id, experiment_id=experiment_id, key=key)
            file_ids.append(file_id)
        return file_ids
