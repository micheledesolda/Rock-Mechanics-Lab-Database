# scripts/test_adding_ultrasonic_waveforms.py
import os
from daos.experiment_dao import ExperimentDao

experiment_id = "s0108sw06car102030"
experiment_dao = ExperimentDao()

dirname = os.path.dirname(__file__)
test_dir = os.path.join(dirname, '../tests/test_data')
file_name = "001_run_in_10MPa.bscan.tsv"
file_path = os.path.join(test_dir,file_name)
experiment_dao.add_utrasonic_waveforms_from_tsv_file(file_path=file_path, experiment_id=experiment_id)