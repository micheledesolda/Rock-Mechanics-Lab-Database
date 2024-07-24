# src/services/machine_service.py
from typing import Dict, Any
from daos.machine_dao import MachineDao
from services.base_service import BaseService

class MachineService(BaseService):
    def __init__(self):
        super().__init__(MachineDao())

    def create_machine(self, machine_id: str, properties: Dict[str, Any], pistons: str) -> str:
        self.dao.create(machine_id, properties, pistons)
        return machine_id
