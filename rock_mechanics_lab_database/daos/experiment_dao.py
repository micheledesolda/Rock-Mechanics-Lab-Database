from typing import List, Dict, Tuple, Optional, Union
import os
import sys
import csv
import json
import gridfs
from nptdms import TdmsFile
from rock_mechanics_lab_database.daos.base_dao import BaseDao
from rock_mechanics_lab_database.daos.block_dao import BlockDao
from rock_mechanics_lab_database.daos.gouge_dao import GougeDao

# Constants
MAXIMUM_DOCUMENT_SIZE = 16000000        # 16 MB, as for mongodb documentation
CHUNK_SIZE = int(MAXIMUM_DOCUMENT_SIZE/8)
MAXIMUM_DIRECT_ENTRY_SIZE = 20000       # 20 KB. Anything above is stored in chunks at most equal CHUNK_SIZE
experiments_collection_name = os.getenv("COLLECTION_EXPERIMENTS") or "Experiments"
vi_data_group_name = os.getenv("VI_DATA_GROUP_NAME") or "ADC"

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
                self.add_gouge(experiment_id=experiment["_id"], gouge_id=gouge["gouge_id"], thickness=gouge["thickness"])
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

    def get_all_experiment_ids(self) -> List[str]:
        """Retrieve all experiment IDs from the database."""
        conn, collection = self._get_connection(self.collection_name)
        try:
            experiments = collection.find({}, {"_id": 1})
            experiment_ids = [str(experiment["_id"]) for experiment in experiments]
            return experiment_ids
        except Exception as err:
            print(f"Error retrieving experiment IDs:\nError: '{err}'")
            return []
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


    def find_centralized_measurements(self, experiment_id: str, group_name: str = vi_data_group_name, channel_name: str = "All") -> Dict:
        """Retrieve centralized measurements and properties for a specific experiment and channel."""
        if (channel_name == "All") and (group_name == vi_data_group_name):
            _, collection = self._get_connection(self.collection_name)

            measurement = collection.find_one(
                {"_id": experiment_id},
                {f"centralized_measurements.{group_name}": 1, "_id": 0}
            )["centralized_measurements"].get(group_name, {})
            channels = {}
            for channel_name in measurement.keys():
                channel_dict = self.find_centralized_measurements(experiment_id=experiment_id, group_name=group_name, channel_name=channel_name)
                channels[channel_name] = channel_dict
            
            return channels

        measurement = self._get_measurement_properties(experiment_id, group_name, channel_name)
        if not measurement:
            return {}
        
        properties = measurement.get("properties", {})
        data = self._get_measurement_data(measurement)
        
        return {"properties": properties, "data": data}
    
    def find_additional_measurements(self, experiment_id: str, measurement_type: str, measurement_sequence_id: str, start_uw: int, end_uw: int) -> Dict:
        """Retrieve additional measurements and properties for a specific experiment and range of uw_numbers."""
        measurement = self._get_additional_measurement_properties(experiment_id, measurement_type, measurement_sequence_id)
        if not measurement:
            return {}

        properties = measurement.get("metadata", {})
        data = self._get_additional_measurement_data(measurement, start_uw, end_uw)

        return {"properties": properties, "data": data}

    # Fetching blocks for a given experiment
    def find_blocks(self, experiment_id: str) -> List[Dict[str, float]]:
        experiment = self.find_experiment_by_id(experiment_id)
        if not experiment:
            return []

        block_dao = BlockDao()
        blocks = []
        for block_entry in experiment.get("blocks", []):
            block = block_dao.find_block_by_id(block_entry["_id"])
            if block:
                blocks.append(block)
        return blocks
        
### Read: helper methods
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
            print(f"Group name: {group_name}\nChannel name: {channel_name}")
            return {}
        finally:
            conn.close()

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

    def _get_additional_measurement_properties(self, experiment_id: str, measurement_type: str, measurement_sequence_id: str)  -> Dict:
        """Retrieve properties of the specified additional measurement."""
        conn, collection = self._get_connection(self.collection_name)
        try:
            measurement = collection.find_one(
                {"_id": experiment_id},
                {f"additional_measurements.{measurement_type}.{measurement_sequence_id}": 1, "_id": 0}
            )["additional_measurements"][measurement_type][measurement_sequence_id]
            return measurement
        except Exception as err:
            print(f"Error retrieving additional measurement properties:\nError: '{err}'")
            return {}
        finally:
            conn.close()

    def _get_additional_measurement_data(self, measurement: Dict, start_uw: int, end_uw: int) -> List:
            """Retrieve data from measurement, either from GridFS or directly."""
            data = []
            try:
                # Data is stored in chunks with IDs containing range information
                file_ids = measurement.get("data", [])
                for file_id in file_ids:
                    chunk_range = self._parse_chunk_range(file_id)
                    if self._is_range_overlapping(chunk_range, (start_uw, end_uw)):
                        chunk = json.loads(self.fs.get(file_id).read())
                        data.extend(self._extract_data_within_range(chunk, start_uw, end_uw))
            except Exception as err:
                print(f"Error retrieving additional measurement data:\nError: '{err}'")
            return data
            
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
        conn, collection = self._get_connection(self.collection_name) 
        blockDao = BlockDao()
        block = blockDao.find_block_by_id(block_id)
        if not block:
            return f"Block with ID {block_id} not found."

        block_entry = {"_id": block_id, "position": position}
        try:
            update_result = collection.update_one(
                {"_id": experiment_id},
                {"$push": {"blocks": block_entry}}
            )
            return f"Block {block_id} added to experiment {experiment_id} at position {position}." if "updated successfully" in update_result else f"Failed to add block {block_id} to experiment {experiment_id}."
        except Exception as err:
            return f"Error adding block to experiment:\nError: '{err}'"

    def add_gouge(self, experiment_id: str, gouge_id: str, thickness: str) -> str:
        """Add a gouge to an experiment."""
        conn, collection = self._get_connection(self.collection_name) 
        gougeDao = GougeDao()
        gouge = gougeDao.find_gouge_by_id(gouge_id)
        if not gouge:
            return f"Gouge with ID {gouge_id} not found."

        gouge_entry = {"_id": gouge_id, "thickness": thickness}
        try:
            update_result = collection.update_one(
                {"_id": experiment_id},
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
            file_name = os.path.basename(file_path).split(".")[0]
            if file_name == experiment_id:
                self.update(experiment_id=experiment_id, update_fields = tdms_dict["properties"])
                self._add_centralized_measurements_from_tdms_dictionary(experiment_id=experiment_id, tdms_dict=tdms_dict)
                print(f"Added measurements from tdms file {file_path} to experiment {experiment_id}")
                return tdms_dict
            else:
                return print(f"Tryng to add to Experiment: {experiment_id}\nmeasurements from another experiment: {file_name}\nProcess aborted")

        except Exception as err:
            print(f"Failed to add measurements from tdms file {file_path} to experiment {experiment_id}:\nError: '{err}'")
            return {}
        finally:
            conn.close()

    def add_utrasonic_waveforms_from_tsv_file(self, experiment_id: str, file_path: str) -> Dict:
        """Store large ultrasonic waveform measurement data in GridFS and update the experiment document."""
        conn, _ = self._get_connection(self.collection_name)

        try:
            tsv_dict = self._read_ultrasonic_waveforms_from_tsv_file(file_path=file_path)
            self._add_ultrasonic_waveforms_from_tsv_dictionary(experiment_id=experiment_id, tsv_dict=tsv_dict)
            print(f"Added Ultrasonic Waveform measurements from tsv file {file_path} to experiment {experiment_id}")
            return tsv_dict
        except Exception as err:
            print(f"Failed to add Ultrasonic Waveform measurements from tsv file {file_path} to experiment {experiment_id}:\nError: '{err}'")
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
                    data_size = sys.getsizeof(data)

                    if data_size > MAXIMUM_DIRECT_ENTRY_SIZE:
                        key = f"{group_name}/{channel_name}/data"
                        file_ids = self._store_centralized_measurement_chunks(experiment_id, key=key, values=data, chunk_size=CHUNK_SIZE)
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

    def _add_ultrasonic_waveforms_from_tsv_dictionary(self, experiment_id: str, tsv_dict: Dict) -> Dict:
            """Extract and store ultrasonic waveform data from a TSV dictionary in GridFS and update the experiment document."""
            conn, _ = self._get_connection(self.collection_name)
            try:
                file_name = tsv_dict.get("file name",{})
                metadata = tsv_dict.get("metadata", {})
                data = tsv_dict.get("data", [])
                data_chunks = {}
                
                total_data_size = 0
                for uw in data:
                    total_data_size += sys.getsizeof(uw)   # getsizeof only read the first level of data structure, that is a list of lists
                print(f"Total data size: {total_data_size}")

                if total_data_size > CHUNK_SIZE:
                    chunk_key = f"ultrasonic_waveforms/{file_name}/uw_numbers"
                    file_ids = self._store_uw_measurement_chunks(experiment_id, key=chunk_key, values=data, chunk_size=CHUNK_SIZE)
                    data_chunks = file_ids
                else:
                    data_chunks = data

                update_fields = {
                    "additional_measurements": {
                            "ultrasonic_waveforms": { 
                                file_name : {
                                    "metadata": metadata,
                                    "data": data_chunks
                            }
                        }
                    }
                }

                update_result = self.update(experiment_id=experiment_id, update_fields=update_fields)
                print(f"Update result: {update_result}")
                return update_result
            except Exception as err:
                print(f"Failed to add Ultrasonic Waveform measurements to experiment {experiment_id}:\nError: '{err}'")
                return {}
            finally:
                conn.close()


    def _read_ultrasonic_waveforms_from_tsv_file(self, file_path: str, encoding: str = 'iso8859') -> Dict[str, List[float]]:
        """Read and parse the measurement file into time series format."""
        try:
            with open(file=file_path, encoding=encoding) as csvfile:
                file_name = os.path.basename(file_path).split(".")[0]
                csvreader = csv.reader(csvfile, delimiter="\t")

                general = next(csvfile).strip("\n").split("|")[0]
                amplitude_scale = next(csvfile).strip("\n").replace(" ","").split("|")[1:]
                time_scale = next(csvfile).strip("\n").replace(" ","").split("|")[1:]
                acquisition_scale = next(csvfile).strip("\n").replace(" ","").split("|")[1:]

                metadata = {
                    "general_info" : general,
                    "amplitude_scale" : amplitude_scale,
                    "time_scale" : time_scale,
                    "acquisition_scale" : acquisition_scale,
                }
                data = []                         # it is going to be a list of lists
                for row in csvreader:  # each row is a uw measurement
                    try:                        
                        data.append( list(map(int, row)))
                    except:                 # this is a clean way to remove the empty lines from that damned tsv file
                        pass
                return {"file name" : file_name, "metadata": metadata, "data": data}
            
        except Exception as err:
            print(f"Error reading file: '{err}'")
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
    def _store_centralized_measurement_chunks(self, experiment_id: str, key: str, values: List, chunk_size: int) -> List[str]:
        """Store chunks of measurement data in GridFS and return the file IDs."""
        chunks = self._split_list(values, chunk_size)
        file_ids = []
        for index, chunk in enumerate(chunks):
            file_id = f"{experiment_id}_{key}_{index}"
            self.fs.put(json.dumps(chunk).encode('utf-8'), _id=file_id, experiment_id=experiment_id, key=key)
            file_ids.append(file_id)
        return file_ids
    
    def _split_list(self, data: List[float], chunk_size: int) -> List[List[float]]:
        """Split a large list of floats into chunks of specified size."""
        return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    def _store_uw_measurement_chunks(self, experiment_id: str, key: str, values: List[List[float]], chunk_size: int) -> List[str]:
        """Store chunks of measurement data in GridFS and return the file IDs."""
        chunks = self._split_list_into_chunks(values, chunk_size)
        file_ids = []
        for index, chunk in enumerate(chunks):
            uw__number_start = index*len(chunk)
            uw__number_end = uw__number_start + len(chunk)
            chunk_range = f"{uw__number_start}-{uw__number_end}"  # the chunk _id contain the information of which uw it contains
            file_id = f"{experiment_id}_{key}_{chunk_range}"
            self.fs.put(json.dumps(chunk).encode('utf-8'), _id=file_id, experiment_id=experiment_id, key=key, range=chunk_range)
            file_ids.append(file_id)
        return file_ids
    
    def _split_list_into_chunks(self, data: List[List[float]], chunk_size: int) -> List[List[List[float]]]:
            """Split a large list of lists into chunks of specified size without splitting individual lists."""
            chunks = []
            current_chunk = []
            current_size = 0

            for row in data:
                row_size = sys.getsizeof(row)
                if current_size + row_size > chunk_size and current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = []
                    current_size = 0

                current_chunk.append(row)
                current_size += row_size

            if current_chunk:
                chunks.append(current_chunk)

            return chunks

    def _parse_chunk_range(self, file_id: str) -> Tuple[int, int]:
        """Parse the range of uw_numbers from the file_id."""
        try:
            range_part = file_id.split("_")[-1]
            start_uw, end_uw = map(int, range_part.split("-"))
            return (start_uw, end_uw)
        except Exception as err:
            print(f"Error parsing chunk range from file_id '{file_id}':\nError: '{err}'")
            return (float('inf'), float('-inf'))

    def _is_range_overlapping(self, chunk_range: Tuple[int, int], target_range: Tuple[int, int]) -> bool:
        """Check if the chunk range overlaps with the target range."""
        chunk_start, chunk_end = chunk_range
        target_start, target_end = target_range
        return not (chunk_end < target_start or chunk_start > target_end)

    def _extract_data_within_range(self, chunk: List[List[float]], start_uw: int, end_uw: int) -> List[List[float]]:
        """Extract data within the specified range from the chunk."""
        return [row for row in chunk if start_uw <= row[0] <= end_uw]


