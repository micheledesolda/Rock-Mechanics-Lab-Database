# rock_mechanics_lab_database/services/machine_service.py

from typing import Dict, Any
from rock_mechanics_lab_database.daos.machine_dao import MachineDao
from rock_mechanics_lab_database.services.base_service import BaseService

class MachineService(BaseService):
    def __init__(self):
        super().__init__(MachineDao())

    def create_machine(self, machine_id: str, machine_type: str, pistons: Dict[str, Any]) -> str:
        self.dao.create(machine_id, machine_type, pistons)
        return machine_id

    def get_machine_by_id(self, machine_id: str) -> Dict[str, Any]:
        return self.dao.find_machine_by_id(machine_id)

    def update_machine(self, machine_id: str, update_fields: Dict[str, Any]) -> str:
        self.dao.update_machine(machine_id, update_fields)
        return machine_id

    def delete_machine(self, machine_id: str) -> str:
        self.dao.delete_machine(machine_id)
        return machine_id

    def add_piston_calibration(self, machine_id: str, piston_name: str, calibration: Dict[str, Any], calibration_date: str) -> str:
        self.dao.add_piston_calibration(machine_id, piston_name, calibration, calibration_date)
        return machine_id

    def add_stiffness_calibration(self, machine_id: str, piston_name: str, stiffness: Dict[str, Any], stiffness_date: str) -> str:
        self.dao.add_stiffness_calibration(machine_id, piston_name, stiffness, stiffness_date)
        return machine_id

    def apply_calibration(self, machine_id: str, piston_name: str, voltage: float, experiment_date: str) -> float:
        return self.dao.apply_calibration(machine_id, piston_name, voltage, experiment_date)

    def apply_stiffness_correction(self, machine_id: str, piston_name: str, force: float, experiment_date: str) -> float:
        return self.dao.apply_stiffness_correction(machine_id, piston_name, force, experiment_date)
