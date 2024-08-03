# src/services/experiment_service.py
from typing import List, Dict, Any
from daos.experiment_dao import ExperimentDao
from services.base_service import BaseService

class ExperimentService(BaseService):
    def __init__(self):
        super().__init__(ExperimentDao())
        
    def create_experiment(self, experiment_id: str, experiment_type: str, gouges: List[Dict]=[], core_sample_id: str="", blocks: List[Dict]=[], centralized_measurements: List[Dict]=[], additional_measurements: List[Dict]=[]) -> str:
        self.dao.create_experiment(experiment_id, experiment_type, gouges, core_sample_id, blocks, centralized_measurements, additional_measurements)
        return experiment_id

    def create_experiment_from_file(self, file_path: str, gouges: List[Dict], blocks: List[Dict]) -> str:
        experiment_id = self.dao.create_experiment_from_file(file_path, gouges, blocks)
        return experiment_id

    def get_experiments(self, offset: int, limit: int) -> List[Dict[str, Any]]:
        return self.dao.read(offset, limit)

    def get_experiment_by_id(self, experiment_id: str) -> Dict[str, Any]:
        return self.dao.find_experiment_by_id(experiment_id)

    def get_centralized_measurements(self, experiment_id: str, group_name: str, channel_name: str) -> Dict:
        return self.dao.find_centralized_measurements(experiment_id, group_name, channel_name)

    def get_additional_measurements(self, experiment_id: str, measurement_type: str, measurement_sequence_id: str, start_uw: int, end_uw: int) -> Dict:
        return self.dao.find_additional_measurements(experiment_id, measurement_type, measurement_sequence_id, start_uw, end_uw)

    def get_blocks(self, experiment_id: str) -> List[Dict[str, float]]:
        return self.dao.find_blocks(experiment_id)

    def update_experiment(self, experiment_id: str, update_fields: Dict[str, Any]) -> str:
        return self.dao.update(experiment_id, update_fields)

    def add_block(self, experiment_id: str, block_id: str, position: str) -> str:
        return self.dao.add_block(experiment_id, block_id, position)

    def add_gouge(self, experiment_id: str, gouge_id: str, thickness: str) -> str:
        return self.dao.add_gouge(experiment_id, gouge_id, thickness)

    def add_centralized_measurements_from_tdms_file(self, experiment_id: str, file_path: str) -> Dict:
        return self.dao.add_centralized_measurements_from_tdms_file(experiment_id, file_path)

    def add_ultrasonic_waveforms_from_tsv_file(self, experiment_id: str, file_path: str) -> Dict:
        return self.dao.add_utrasonic_waveforms_from_tsv_file(experiment_id, file_path)

    def delete_experiment(self, experiment_id: str) -> str:
        return self.dao.delete(experiment_id)
