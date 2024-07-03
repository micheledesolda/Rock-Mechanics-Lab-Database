import pymongo
from typing import List, Dict, Optional, Union, Tuple, Any
import os
import sys
import csv
import json
import gridfs
from nptdms import TdmsFile
import matplotlib.pyplot as plt

# MongoDB connection details
url = os.getenv("MONGO_URL") or "mongodb://localhost:27017/"
db_name = os.getenv("DB_NAME") or "EPS"
experiments_collection_name = os.getenv("COLLECTION_EXPERIMENTS") or "Experiments"
sensors_collection_name = os.getenv("COLLECTION_SENSORS") or "Sensors"
blocks_collection_name = os.getenv("COLLECTION_BLOCKS") or "Blocks"
gouges_collection_name = os.getenv("COLLECTION_GOUGES") or "Gouges"
coresamples_collection_name = os.getenv("COLLECTION_CORESAMPLES") or "CoreSamples"
machines_collection_name = os.getenv("COLLECTION_MACHINES") or "Machines"

class BaseDao:
    def __init__(self):
        """Initialize the BaseDao class with database connection details."""
        self.url = url
        self.db_name = db_name

    def _get_connection(self, collection_name: str) -> Tuple[pymongo.MongoClient, pymongo.collection.Collection]:
        """Create a new connection to the MongoDB database and return the collection."""
        conn = pymongo.MongoClient(self.url)
        db = conn[self.db_name]
        collection = db[collection_name]
        return conn, collection

    def create(self, collection_name: str, document: Dict[str, Any]) -> str:
        """Create a new document in the specified collection."""
        conn, collection = self._get_connection(collection_name)
        try:
            result = collection.insert_one(document)
            print(f"Document {result.inserted_id} added to {collection_name}.")
            return str(result.inserted_id)
        except Exception as err:
            print(f"Error: '{err}'")
            return ''
        finally:
            conn.close()

    def read(self, collection_name: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Read a document from the specified collection."""
        conn, collection = self._get_connection(collection_name)
        try:
            document = collection.find_one(query)
            return document
        except Exception as err:
            print(f"Error: '{err}'")
            return None
        finally:
            conn.close()

    def update(self, collection_name: str, query: Dict[str, Any], update_values: Dict[str, Any]) -> bool:
        """Update a document in the specified collection."""
        conn, collection = self._get_connection(collection_name)
        try:
            result = collection.update_one(query, {"$set": update_values})
            if result.modified_count > 0:
                print(f"Document updated in {collection_name}.")
                return True
            else:
                print(f"No document matched the query in {collection_name}.")
                return False
        except Exception as err:
            print(f"Error: '{err}'")
            return False
        finally:
            conn.close()

    def delete(self, collection_name: str, query: Dict[str, Any]) -> bool:
        """Delete a document from the specified collection."""
        conn, collection = self._get_connection(collection_name)
        try:
            result = collection.delete_one(query)
            if result.deleted_count > 0:
                print(f"Document deleted from {collection_name}.")
                return True
            else:
                print(f"No document matched the query in {collection_name}.")
                return False
        except Exception as err:
            print(f"Error: '{err}'")
            return False
        finally:
            conn.close()

class Machine(BaseDao):
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


class GougeDao(BaseDao):
    def __init__(self):
        """Initialize the GougeDao class with a connection to the MongoDB database."""
        super().__init__()
        self.collection_name = gouges_collection_name

    def create(self, gouge_id: str, material: str, grain_size_mum: float) -> None:
        """Create a new gouge in the database."""
        conn, collection = self._get_connection(self.collection_name)

        gouge = {
            "_id": gouge_id,
            "material": material,
            "grain_size_mum": grain_size_mum
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

class SensorDao(BaseDao):
    available_sensors = [
        {"_id": "PZT_1", "type": "piezoelectric", "model": "P-871.20", "frequency": 1.0, "properties": {"material": "PZT"}},
        {"_id": "PZT_2", "type": "piezoelectric", "model": "P-871.30", "frequency": 3.0, "properties": {"material": "PZT"}},
        {"_id": "PZT_3", "type": "piezoelectric", "model": "P-871.40", "frequency": 5.0, "properties": {"material": "PZT"}}
    ]
    
    def __init__(self):
        """Initialize the SensorDao class with a connection to the MongoDB database."""
        super().__init__()
        self.collection_name = sensors_collection_name
        
    def initialize_inventory(self) -> None:
        """Initialize the sensor inventory in the database."""
        conn, collection = self._get_connection(self.collection_name)

        try:
            for sensor in self.available_sensors:
                collection.update_one({"_id": sensor["_id"]}, {"$set": sensor}, upsert=True)
            print("Sensor inventory initialized.")
        except Exception as err:
            print(f"Error: '{err}'")
        finally:
            conn.close()

    def find_sensor_by_id(self, _id: str) -> Optional[Dict]:
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

class ExperimentDao(BaseDao):
    def __init__(self):
        """Initialize the ExperimentDao class with a connection to the MongoDB database."""
        super().__init__()
        self.collection_name = experiments_collection_name
        conn, _ = self._get_connection(self.collection_name)
        db = conn[self.db_name]
        self.fs = gridfs.GridFS(db)  # For storing measurement and SPLIT IN CHUNKS TOO BIG DATA
    
    def create(self, experiment_id: str="", experiment_type: str = "", gouges: List[dict] = [], core_sample_id: str = None, 
               blocks: List[Dict] = [], centralized_measurements: List[Dict] = [], additional_measurements: List[Dict] = []) -> str:
        """Create a new experiment in the database."""
        conn, collection = self._get_connection(self.collection_name)

        experiment = {
                    "_id": experiment_id,
                    "experiment_type": experiment_type,
                    "gouges": [],
                    "core_sample_id": core_sample_id,    # to be implemented with an "add_core" when we will start with triaxial
                    "blocks": [],
                    "centralized_measurements": centralized_measurements,
                    "additional_measurements": additional_measurements
                    }

        if os.path.isfile(experiment_id):
            # if the id passed is a path to file, then the experiment must be build with the info of the file.
            # Here we handle the case where the file is a tdms from Labview interface
            s = f"Passed an existing file path as experiment_id\nExtracting information from:\n\t{experiment_id}"
            print(s)
            try:
                tdms_dict = self.read_experiment_tdms_file(file_path=experiment_id)
                experiment["_id"] = os.path.basename(experiment_id).split(".")[0]        # file name without extension. We force the _id to be the name of the tdms file
                experiment.update(tdms_dict["properties"])
                experiment_insert = collection.insert_one(experiment)
                self.add_centralized_measurements_from_tdms_dictionary(experiment_id=experiment["_id"],tdms_dict=tdms_dict)
            except Exception as err:
                s = f"Adding experiment {experiment_id}\n\t:Error: '{err}'"
        else:
            experiment_insert = collection.insert_one(experiment)
        
        try:
            for block in blocks:
                self.add_block(experiment_id=experiment["_id"],block_id = block['block_id'], position= block['position'])

            for gouge in gouges:
                self.add_gouge(experiment_id=experiment["_id"],gouge_id= gouge["gouge_id"], thickness_mm = gouge["thickness_mm"])

            s = f"Experiment {experiment_insert.inserted_id} added to database"

            return experiment["_id"]
        
        except Exception as err:
            s = f"Adding experiment {experiment_id} to database failed!\n\tError: '{err}'"
        finally:
            print(s)
            conn.close()


    
    def read(self, offset: int, limit: int) -> Union[List[Dict], str]:
        """Read experiments from the database with pagination."""
        conn, collection = self._get_connection(self.collection_name)
        try:
            experiments = collection.find().skip((offset - 1) * limit).limit(limit)
            
            experiment_list = []
            for experiment in experiments:
                experiment['_id'] = str(experiment['_id'])  # Convert ObjectId to string
                experiment_list.append(experiment)
            
            if not experiment_list:
                s = "No experiments found"
                print(s)
                conn.close()
                return s
            
            return experiment_list
            
        except Exception as err:
            return f"Error: '{err}'"
        finally:
            conn.close()   


    def find_experiment_by_id(self, experiment_id: str) -> Optional[Dict]:
        """Retrieve sensor details by sensor ID."""
        conn, collection = self._get_connection(self.collection_name)
        try:
            experiment = collection.find_one({"_id": experiment_id})
            s = f"Experiment {experiment_id} found\n"
            print(s)
            return experiment
        except Exception as err:
            s = f"Experiment {experiment_id} not found\n"
            print(s)
            print(f"Error: '{err}'")
            return None
        finally:
            conn.close()   

    def find_centralized_measurements(self, experiment_id: str, group_name: str, channel_name: str) -> Dict:
        """Retrieve centralized measurements and properties for a specific experiment and channel.

        Args:
            experiment_id (str): The ID of the experiment.
            group_name (str): The name of the group.
            channel_name (str): The name of the channel.

        Returns:
            Dict: A dictionary containing properties and data.
        """
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
            if isinstance(measurement["data"], list):
                # Data is stored in chunks
                file_ids = measurement["data"]
                for file_id in file_ids:
                    chunk = json.loads(self.fs.get(file_id).read())
                    data.extend(chunk)
            else:
                # Data is stored directly in the document
                data = measurement["data"]

            return {"properties": properties, "data": data}
        except Exception as err:
            print(f"Error: '{err}'")
            return {}
        finally:
            conn.close()
  

    def update(self, experiment_id: str, update_fields: Dict) -> str:
        """Update an experiment in the database."""
        conn, collection = self._get_connection(self.collection_name) 
        try:
            update_result = collection.update_one({"_id": experiment_id}, {"$set": update_fields})

            if update_result.modified_count > 0:
                return f"Experiment {experiment_id} updated successfully"
            else:
                return f"No changes made to experiment {experiment_id}"
        except Exception as err:
            return f"Error: '{err}'"
        finally:
            conn.close()   

    def add_block(self, experiment_id: str, block_id: str, position: str) -> None:
        """Add a block to an experiment."""
        blockDao = BlockDao()
        block = blockDao.find_block_by_id(block_id)
        conn, collection = self._get_connection(self.collection_name)

        if block is None:
            s = f"Block with ID {block_id} not found."
            print(s)
            conn.close()   
            return s

        block_entry = {
            "_id": block_id,
            "position": position
        }

        try:
            update_result = collection.update_one(
                {"_id": experiment_id},
                {"$push": {"blocks": block_entry}}
            )

            if update_result.modified_count > 0:
                s = f"Block {block_id} added to experiment {experiment_id} at position {position}."
                print(s)
                return s
            else:
                s = f"Failed to add block {block_id} to experiment {experiment_id}."
                print(s)
                return s
        except Exception as err:
            s = f"Error adding block to experiment: '{err}'"
            print(s)
            return s
        finally:
            conn.close() 

    def add_gouge(self, experiment_id: str, gouge_id: str, thickness_mm: str) -> str:
        """Add a gouge to an experiment."""
        conn, collection = self._get_connection(self.collection_name)
        gougeDao = GougeDao()
        gouge = gougeDao.find_gouge_by_id(gouge_id)

        if gouge is None:
            s = f"Gouge with ID {gouge_id} not found."
            print(s)
            conn.close() 
            return s
        
        gouge_entry = {
            "_id" : gouge_id,
            "thickness_mm" : thickness_mm
        }

        try:
            collection.update_one({"_id": experiment_id}, {"$push": {"gouges": gouge_entry}})
            print(f"Gouge {gouge_id} added to experiment {experiment_id}.")
        except Exception as err:
            print(f"Error: '{err}'")
        finally:
            conn.close() 

    # Since the centralized_measurement can be a really big file: store chunks in GridFS
    def add_centralized_measurements_from_tdms_file(self, experiment_id: str, file_path: str) -> Dict:
        """Store large TDMS measurement data in GridFS and update the experiment document.

        Args:
            experiment_id (str): The ID of the experiment.
            file_path (str): Path to the TDMS file containing the measurement data.

        Returns:
            Dict: Mapping of measurement names to file IDs.
        """
        conn, _ = self._get_connection(self.collection_name)

        chunk_size = 10000
        data_chunk = {}

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
        """Extract and store centralized measurements from a TDMS dictionary in GridFS and update the experiment document.

        Args:
            experiment_id (str): The ID of the experiment.
            tdms_dict (Dict): Dictionary containing TDMS data.

        Returns:
            Dict: Mapping of measurement names to file IDs.
        """
        conn, _ = self._get_connection(self.collection_name)

        try:
            chunk_size = 10000
            data_chunk = {}
            for group_name, group_data in tdms_dict['groups'].items():
                for channel_name, channel_data in group_data['channels'].items():
                    # save the data in chunk
                    data = channel_data['data']
                    properties = channel_data['properties']

                    if sys.getsizeof(data)> chunk_size:
                        key = f"{group_name}/{channel_name}/data"        # the key for the data chunks
                        file_ids = self.store_measurement_chunks(experiment_id, key=key, values=data, chunk_size=chunk_size)
                        if group_name not in data_chunk:
                            data_chunk[group_name] = dict()
                        data_chunk[group_name][channel_name] = dict()
                        data_chunk[group_name][channel_name]["properties"] = properties
                        data_chunk[group_name][channel_name]["data"] = file_ids

                    else:
                        if group_name not in data_chunk:
                            data_chunk[group_name] = dict()
                        data_chunk[group_name][channel_name] = dict()
                        data_chunk[group_name][channel_name]["properties"] = properties
                        data_chunk[group_name][channel_name]["data"] = data


            self.update(experiment_id=experiment_id, update_fields={"centralized_measurements": data_chunk})
            return

        except Exception as err:
            s = "Measurement data not added to database:\n"
            print(s + f"\tError: '{err}'")
            return {}
        finally:
            conn.close()


    def read_experiment_tdms_file(self, file_path: str) -> Dict[str, List[float]]:
        """Read and parse the measurement file into time series format.
        
        Args:
            file_path (str): Path to the measurement file.
        
        Returns:
            Dict[str, List[float]]: Parsed time series data.
        """
        conn, _ = self._get_connection(self.collection_name)  

        try:
            tdms_file = TdmsFile.read(file_path)
            tdms_dict = {}
            # Add general properties of the TDMS file
            tdms_dict['properties'] = {key: value for key, value in tdms_file.properties.items()}

            # Iterate over groups and channels to populate the dictionary
            tdms_dict['groups'] = {}

            for group in tdms_file.groups():
                group_dict = {'channels': {}}
                
                for channel in group.channels():
                    channel_dict = {
                        'properties': {key: value for key, value in channel.properties.items()},
                        'data': channel.data.tolist()  # Convert numpy array to list
                    }
                    group_dict['channels'][channel.name] = channel_dict
                
                tdms_dict['groups'][group.name] = group_dict
            return tdms_dict
        
        except Exception as err:
            print(f"Error reading file\n: '{err}'")
            return {}
        finally:
            conn.close()

    def add_centralized_measurements_from_reduced_file(self, experiment_id: str, file_path: str) -> Dict:
        """Store large measurement data in GridFS and update the experiment document."""
        conn, _ = self._get_connection(self.collection_name)

        chunk_size = 10000                 # a value smoller than 16 Mb. To be parametrized in the future
        data_chunk = {}

        try:
            time_series_data = self.read_experiment_reduced_file(file_path)

            for key, values in time_series_data.items():
                file_ids = self.store_measurement_chunks(experiment_id, key, values, chunk_size)
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
        """Read and parse the measurement file into time series format.
        
        Args:
            file_path (str): Path to the measurement file.
        
        Returns:
            Dict[str, List[float]]: Parsed time series data.
        """
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
        
    ######### Utilities ##################
    def split_list(self, data: List[float], chunk_size: int) -> List[List[float]]:
        """Split a large list of floats into chunks of specified size.
        
        Args:
            data (List[float]): The list of floats to be split into chunks.
            chunk_size (int): The size of each chunk.
        
        Returns:
            List[List[float]]: A list of lists, where each inner list contains floats of length <= chunk_size.
        """
        return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
    
    def store_measurement_chunks(self, experiment_id: str, key: str, values: List, chunk_size: int) -> List:
        """Store chunks of measurement data in GridFS and return the file IDs."""
        chunks = self.split_list(values, chunk_size)
        file_ids = []
        for chunk in chunks:
            file_id = self.fs.put(json.dumps(chunk).encode('utf-8'), experiment_id=experiment_id, key=key)
            file_ids.append(file_id)
        return file_ids
    
##############################################################################
    def delete(self, experiment_id: str) -> str:
        """Delete an experiment from the database."""
        conn, collection = self._get_connection(self.collection_name)
        try:
            delete_result = collection.delete_one({"_id": experiment_id})
            if delete_result.deleted_count > 0:
                return f"Experiment {experiment_id} deleted from database\\n"
            else:
                return f"Experiment {experiment_id} not found\n"
        except Exception as err:
            return f"Error: '{err}'"
        finally:
            conn.close()

## USAGE EXAMPLESs
# Generic examples for BaseDao class: use of CRUD methods  
document = {
 "_id": "doc1",
 "name": "Sample Document",
 "type": "example",
 "value": 123
}
collection_name = "a generic collection name"
query = {"_id": "doc1"}
update_values = {"value": 456}                      

base_dao = BaseDao()
doc_id = base_dao.create(collection_name=collection_name, document=document )    # Create a document in a collection of the database
document = base_dao.read(collection_name, query)                                 # Read the collection for the correspondent query
update_result = base_dao.update(collection_name, query, update_values)           # Udate the field "value" of the document
delete_result = base_dao.delete(collection_name, query)                          # Delete the document from database

# Initialize and populate the database with sensor inventory
sensorDao = SensorDao()
sensorDao.initialize_inventory()

# # Add some core samples and gouges
coreSampleDao = CoreSampleDao()
coreSampleDao.create(core_sample_id="san_donato_1", material="granite", dimensions={"diameter": 5.0, "height": 10.0})

gougeDao = GougeDao()
gougeDao.create(gouge_id="mont1", material="montmorillonite", grain_size_mum=125)

# # Example usage to create blocks
blockDao = BlockDao()
blockDao.create(block_id="paglialberi_1", material="steel", dimensions={"width": 2.0, "height": 2.0, "depth": 4.8}, sensor_rail_width=0.5)
blockDao.create(block_id="paglialberi_2", material="steel", dimensions={"width": 2.0, "height": 2.0, "depth": 4.8}, sensor_rail_width=0.5)
blockDao.create(block_id="mem_1", material="steel", dimensions={"width": 2.0, "height": 2.0, "depth": 4.8}, sensor_rail_width=0.5)
# Example usage to add sensors to a block
blockDao.add_sensor(block_id="paglialberi_1", sensor_id="PZT_1", sensor_name="S_left", position={"x": 0.5, "y": 1.0, "z": 0.2}, orientation="left", calibration="Calibration S_left")
blockDao.add_sensor(block_id="paglialberi_1", sensor_id="PZT_1", sensor_name="S_right", position={"x": 0.7, "y": 1.0, "z": 0.2}, orientation="up", calibration="Calibration S_right")
blockDao.add_sensor(block_id="paglialberi_2", sensor_id="PZT_2", sensor_name="P", position={"x": 1.5, "y": 1.0, "z": 0.2}, orientation=None, calibration="Calibration P")

# Example usage to create experiment: look at the different behaviour if the experiment_id is the actual path to data
experimentDao = ExperimentDao()
experiment_dir = "/home/michele/Desktop/Dottorato/active_source_implementation/experiments_Brava_2/s0108/mechanical_data"
experiment_name = "s0108sw06car102030.tdms"
experiment_path = os.path.join(experiment_dir,experiment_name)
experiment_id = experimentDao.create(experiment_id=experiment_path, experiment_type="double direct shear", blocks=[{"block_id":"paglialberi_1","position":"left"}], gouges=[{"gouge_id":"mont1","thickness_mm":0.3}], centralized_measurements=[1, 2, 3],  additional_measurements=[{"amplitude_uw_mum":[10, 11, 12]},{"emission_rate_ae":[12,5,28,0,0,31]}])
experimentDao.create(experiment_id="2", experiment_type="triaxial", core_sample_id=["san_donato_1"], centralized_measurements=[{"time_s":[1,2,3]},{"displacement_mum":[3,4.5,6.3]}], additional_measurements=[{"amplitude_uw_mum":[10, 11, 12]},{"emission_rate_ae":[12,5,28,0,0,31]}])

# Example usage to add blocks, gouge or measurement to the experiments
experimentDao.add_block(experiment_id=experiment_id, block_id="paglialberi_1",position="left")
experimentDao.add_gouge(experiment_id=experiment_id,gouge_id="mont1",thickness_mm=0.3)
experimentDao.add_block(experiment_id=experiment_id, block_id="paglialberi_2",position="right")
# Data can be added after the experiment creation
experimentDao.add_centralized_measurements_from_tdms_file(experiment_id=experiment_id,file_path=experiment_path)
# Example Queries to experiments
experimentDao.read(offset=1, limit=10)
experimentDao.update(experiment_id="2", update_fields={"centralized_measurements": [4, 11], "additional_measurements": [8, 7, 3]})
experimentDao.delete(experiment_id="2")
experiment  = experimentDao.find_experiment_by_id(experiment_id="s0108sw06car102030")
for key, value in experiment.items():
    print(key,value)

# x_field = "Time"
# y_field = "Vertical Load"
# x_dict = experimentDao.find_centralized_measurements(experiment_id=experiment_id, group_name="ADC", channel_name=x_field)
# y_dict = experimentDao.find_centralized_measurements(experiment_id=experiment_id, group_name="ADC", channel_name=y_field)
# x_values = x_dict["data"]
# y_values = y_dict["data"]

# # Create scatter plot
# plt.plot(x_values, y_values)
# plt.xlabel(x_field)
# plt.ylabel(y_field)
# plt.title(f'Plot of {x_field} vs {y_field}')
# plt.show()

# print("Database created and data added successfully.")
