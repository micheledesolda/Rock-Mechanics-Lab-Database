# src/services/experiment_service.py

from typing import List, Dict, Any
from daos.experiment_dao import ExperimentDao
from models.experiment_model import Experiment

class ExperimentService:
    def __init__(self):
        self.experiment_dao = ExperimentDao()

    def create_experiment(self, experiment: Experiment) -> str:
        return self.experiment_dao.create(
            experiment_id=experiment.experiment_id or "",
            experiment_type=experiment.experiment_type or "",
            gouges=[gouge.model_dump() for gouge in experiment.gouges] if experiment.gouges else [],
            core_sample_id=experiment.core_sample_id,
            blocks=[block.model_dump() for block in experiment.blocks] if experiment.blocks else [],
            centralized_measurements=experiment.centralized_measurements or {},
            additional_measurements=experiment.additional_measurements or {}
       )

    def create_experiment_from_file(self, file_path: str) -> str:
        return self.experiment_dao.create_experiment_from_file(
            file_path=file_path,
            gouges=[],
            blocks=[]
        )


    def get_experiments(self, offset: int, limit: int) -> List[Dict[str, Any]]:
        return self.experiment_dao.read(offset=offset, limit=limit)
    
    def get_experiment_by_id(self, experiment_id: str) -> List[Dict[str, Any]]:
        return self.experiment_dao.find_experiment_by_id(experiment_id=experiment_id)

    def get_centralized_measurements(self, experiment_id: str, group_name: str, channel_name: str) -> Dict:
            return self.experiment_dao.find_centralized_measurements(experiment_id, group_name, channel_name)




