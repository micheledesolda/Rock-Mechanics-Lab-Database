# Functions to read and upload reduced file instead of directly tdms
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