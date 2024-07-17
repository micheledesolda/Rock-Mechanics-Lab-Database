# src/daos/experiment_dao.py
from typing import List, Dict, Optional, Union, Any
import os
import sys
import csv
import json
import gridfs
from nptdms import TdmsFile
from daos.base_dao import BaseDao
from daos.block_dao import BlockDao
from daos.gouge_dao import GougeDao

# MongoDB connection details
url = os.getenv("MONGO_URL") or "mongodb://localhost:27017/"
db_name = os.getenv("DB_NAME") or "EPS"
experiments_collection_name = os.getenv("COLLECTION_EXPERIMENTS") or "Experiments"

# work out these constants according to real limits value/query performance
MAXIMUM_SIZE = 16000000 # 16 Mb is the maximum uplading mongodb handles
CHUNK_SIZE = int(MAXIMUM_SIZE/64) # at worst, we will upload floats (8 bytes) arrays of this length

class ExperimentDao(BaseDao):
    def __init__(self):
        """Initialize the ExperimentDao class with a connection to the MongoDB database."""
        super().__init__()
        self.collection_name = experiments_collection_name
        conn, _ = self._get_connection(self.collection_name)
        db = conn[self.db_name]
        self.fs = gridfs.GridFS(db)  # For storing measurement and SPLIT IN CHUNKS TOO BIG DATA
    
    def create_experiment(self, experiment_id: str="", experiment_type: str="", gouges: List[dict]=[], 
                          core_sample_id: str=None, blocks: List[Dict]=[], centralized_measurements: List[Dict]=[], 
                          additional_measurements: List[Dict]=[]) -> str:
        conn, collection = self._get_connection(self.collection_name)
        experiment = {
            "_id": experiment_id,
            "experiment_type": experiment_type,
            "gouges": [],
            "core_sample_id": core_sample_id,
            "blocks": [],
            "centralized_measurements": centralized_measurements,
            "additional_measurements": additional_measurements
        }

        collection.insert_one(experiment)

        try:
            for block in blocks:
                self.add_block(experiment_id=experiment["_id"], block_id=block['block_id'], position=block['position'])
            for gouge in gouges:
                self.add_gouge(experiment_id=experiment["_id"], gouge_id=gouge["gouge_id"], thickness_mm=gouge["thickness_mm"])

            return experiment["_id"]
        
        except Exception as err:
            print(f"Adding experiment {experiment_id} to database failed!\n\tError: '{err}'")
            return ""
        
        finally:
            conn.close()

    def create_experiment_from_file(self, file_path: str, gouges: List[dict]=[], blocks: List[Dict]=[]) -> str:
        """Create a new experiment from a file."""
        if not os.path.isfile(file_path):
            raise ValueError(f"File path {file_path} is not a valid file path")

        conn, collection = self._get_connection(self.collection_name)
        experiment_id = os.path.basename(file_path).split(".")[0]
     
        try:
            tdms_dict = self.read_experiment_tdms_file(file_path=file_path)
            experiment = {
                "_id": experiment_id,
                "experiment_type": tdms_dict.get("experiment_type", ""),
                "gouges": [],
                "core_sample_id": None,
                "blocks": [],
                "centralized_measurements":  [],
                "additional_measurements": []
            }

            experiment.update(tdms_dict["properties"])
            collection.insert_one(experiment)
            self.add_centralized_measurements_from_tdms_dictionary(experiment_id=experiment["_id"], tdms_dict=tdms_dict)
            
            for block in blocks:
                self.add_block(experiment_id=experiment["_id"], block_id=block['block_id'], position=block['position'])
            for gouge in gouges:
                self.add_gouge(experiment_id=experiment["_id"], gouge_id=gouge["gouge_id"], thickness_mm=gouge["thickness_mm"])

            return experiment["_id"]
        
        except Exception as err:
            print(f"Adding experiment from file:\n\t{file_path} failed!\n\tError: '{err}'")
            return ""
        
        finally:
            conn.close()

    def read(self, offset: int, limit: int) -> Union[List[Dict], str]:
        """Read experiments from the database with pagination."""
        try:
            conn, collection = self._get_connection(self.collection_name)
            experiments = collection.find().skip((offset - 1) * limit).limit(limit)
            experiment_list = [{'_id': str(experiment['_id']), **experiment} for experiment in experiments]            
            return experiment_list if experiment_list else "No experiments found"

        except Exception as err:
            return f"Something went wrong reading experiments from database:\n\tError: '{err}'"
        finally:
            conn.close()   
        
    def find_experiment_by_id(self, experiment_id: str) -> Optional[Dict]:
        """Retrieve epxeriment details by sensor ID."""
        conn, collection = self._get_connection(self.collection_name)
        try:
            experiment = collection.find_one({"_id": experiment_id})
            s = f"Experiment {experiment_id} found\n"
            print(s)
            return experiment
        except Exception as err:
            print(f"Experiment {experiment_id} not found\nError: '{err}'")
            return None
        finally:
            conn.close()   
        
    def find_centralized_measurements(self, experiment_id: str, group_name: str, channel_name: str) -> Dict:
        """Retrieve centralized measurements and properties for a specific experiment and channel."""
        conn, collection = self._get_connection(self.collection_name)
        try:
            # Retrieve the centralized measurements for the specified group and channel
            measurement = collection.find_one(
                {"_id": experiment_id},
                {f"centralized_measurements.{group_name}.{channel_name}": 1, "_id": 0}
            )["centralized_measurements"][group_name][channel_name]

            properties = measurement["properties"]
            data = []

            # Check if the data is stored as chunks in GridFS or directly in the document
            try: 
                # Data is stored in chunks
                file_ids = measurement["data"]
                for file_id in file_ids:
                    print(file_id)
                    chunk = json.loads(self.fs.get(file_id).read())
                    data.extend(chunk)
            except:
                # Data is stored directly in the document
                data = measurement["data"]

            return {"properties": properties, "data": data}
        except Exception as err:
            print(f"Data not retrieved:\n\tError: '{err}'")
            return {}
        finally:
            conn.close()
  

    def update(self, experiment_id: str, update_fields: Dict) -> str:
        """Update an experiment in the database."""
        conn, collection = self._get_connection(self.collection_name) 
        try:
            update_result = collection.update_one({"_id": experiment_id}, {"$set": update_fields})
            return f"Experiment {experiment_id} updated successfully" if update_result.modified_count > 0 else f"No changes made to experiment {experiment_id}"
        except Exception as err:
            return f"Error: '{err}'"
        finally:
            conn.close()  
        
    def add_block(self, experiment_id: str, block_id: str, position: str) -> str:
        """Add a block to an experiment."""
        conn, collection = self._get_connection(self.collection_name) 
        blockDao = BlockDao()
        block = blockDao.find_block_by_id(block_id)
        if block is None:
            return f"Block with ID {block_id} not found."

        block_entry = {"_id": block_id, "position": position}
        try:
            update_result = collection.update_one(
                {"_id": experiment_id},
                {"$push": {"blocks": block_entry}}
            )
            return f"Block {block_id} added to experiment {experiment_id} at position {position}." if update_result.modified_count > 0 else f"Failed to add block {block_id} to experiment {experiment_id}."
        except Exception as err:
            return f"Error adding block to experiment: '{err}'"
        finally:
            conn.close() 
            
    def add_gouge(self, experiment_id: str, gouge_id: str, thickness_mm: str) -> str:
        """Add a gouge to an experiment."""
        conn, collection = self._get_connection(self.collection_name)
        gougeDao = GougeDao()
        gouge = gougeDao.find_gouge_by_id(gouge_id)
        if gouge is None:
            return f"Gouge with ID {gouge_id} not found."

        gouge_entry = {"_id": gouge_id, "thickness_mm": thickness_mm}
        try:
            collection = self.db[self.collection_name]
            collection.update_one({"_id": experiment_id}, {"$push": {"gouges": gouge_entry}})
            return f"Gouge {gouge_id} added to experiment {experiment_id}."
        except Exception as err:
            return f"Error: '{err}'"
        finally:
            conn.close() 

    # Since the centralized_measurement can be a really big file: store chunks in GridFS
    def add_centralized_measurements_from_tdms_file(self, experiment_id: str, file_path: str) -> Dict:
        """Store large TDMS measurement data in GridFS and update the experiment document."""
        conn, _ = self._get_connection(self.collection_name)

        try:
            tdms_dict = self.read_experiment_tdms_file(file_path=file_path)
            self.add_centralized_measurements_from_tdms_dictionary(experiment_id=experiment_id, tdms_dict=tdms_dict)    
            s = f"Added to experiment {experiment_id} measurements from tdms file:\n\t {file_path}"
            print(s)

        except Exception as err:
            s = f"Failed to add to {experiment_id} measurements from tdms file in\n:\t{file_path}\n"
            print(s + f"\tError: '{err}'")
            return {}
        finally:
            conn.close()

    def add_centralized_measurements_from_tdms_dictionary(self, experiment_id: str, tdms_dict: Dict) -> Dict:
        """Extract and store centralized measurements from a TDMS dictionary in GridFS and update the experiment document."""
        conn, _ = self._get_connection(self.collection_name)
        try:
            data_chunk = {}
            for group_name, group_data in tdms_dict['groups'].items():
                for channel_name, channel_data in group_data['channels'].items():
                    data = channel_data['data']
                    properties = channel_data['properties']

                    print(f"{channel_name} {sys.getsizeof(data)}")
                    if len(data) > CHUNK_SIZE:
                        key = f"{group_name}/{channel_name}/data"  # Key for the data chunks
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
            print(f"Update result: {update_result}")  # Debugging print to check the update result
            return update_result

        except Exception as err:
            print(f"Measurement data not added to database:\n\tError: '{err}'")
            return {}
        finally:
            conn.close()

    def read_experiment_tdms_file(self, file_path: str) -> Dict[str, List[float]]:
        """Read and parse the measurement file into time series format."""
        conn, _ = self._get_connection(self.collection_name)  

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
            print(f"Error reading file\n: '{err}'")
            return {}
        finally:
            conn.close()

    def add_centralized_measurements_from_reduced_file(self, experiment_id: str, file_path: str) -> Dict:
        """Store large measurement data in GridFS and update the experiment document."""
        conn, _ = self._get_connection(self.collection_name)
        data_chunk = {}

        try:
            time_series_data = self.read_experiment_reduced_file(file_path)

            for key, values in time_series_data.items():
                file_ids = self._store_measurement_chunks(experiment_id, key, values, chunk_size=CHUNK_SIZE)
                data_chunk[key] = file_ids

            self.update(experiment_id=experiment_id, update_fields={"centralized_measurements": data_chunk})
            return data_chunk

        except Exception as err:
            s = "Measurements file not added to database:\n"
            print(s + f"    Error: '{err}'")
            return {}
        finally:
            conn.close()

    def read_experiment_reduced_file(self, file_path: str) -> Dict[str, List[float]]:
        """Read and parse the measurement file into time series format."""
        try:
            with open(file_path, mode='r') as file:
                csv_reader = csv.DictReader(file, delimiter='\t')
                
                # Initialize time_series_data dictionary from the first row (header)
                fieldnames = csv_reader.fieldnames
                time_series_data = {field: [] for field in fieldnames}
                
                # Read and parse the rows
                for row in csv_reader:
                    for key in time_series_data.keys():
                        time_series_data[key].append(float(row[key]))
            return time_series_data
        except Exception as err:
            print(f"Error reading file: '{err}'")
            return {}

    def delete(self, experiment_id: str) -> str:
        """Delete an experiment from the database."""
        conn, collection = self._get_connection(self.collection_name)
        try:
            delete_result = collection.delete_one({"_id": experiment_id})
            return f"Experiment {experiment_id} deleted from database\\n" if delete_result.deleted_count > 0 else f"Experiment {experiment_id} not found\n"

        except Exception as err:
            return f"Error: '{err}'"
        finally:
            conn.close()

    ######### Utilities ##################
    def _split_list(self, data: List[float], chunk_size: int) -> List[List[float]]:
        """Split a large list of floats into chunks of specified size."""
        return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
    
    def _store_measurement_chunks(self, experiment_id: str, key: str, values: List, chunk_size: int) -> List[str]:
        """Store chunks of measurement data in GridFS and return the file IDs."""
        chunks = self._split_list(values, chunk_size)
        file_ids = []
        for index, chunk in enumerate(chunks):
            # file_id is a string. This avoid problem on serialization. The way the strings are made should make them unique
            file_id = f"{experiment_id}_{key}_{index}"
            self.fs.put(json.dumps(chunk).encode('utf-8'), _id=file_id, experiment_id=experiment_id, key=key)
            file_ids.append(file_id)
        return file_ids
   