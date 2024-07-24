# src/services/gouge_service.py
from typing import Dict, Any
from daos.gouge_dao import GougeDao
from services.base_service import BaseService

class GougeService(BaseService):
    def __init__(self):
        super().__init__(GougeDao())

    def create_gouge(self, gouge_id: str, thickness_mm: str, grain_size_mum: str) -> str:
        self.dao.create(gouge_id, thickness_mm, grain_size_mum)
        return gouge_id

    def get_gouge(self, gouge_id: str) -> Dict[str, Any]:
        return self.dao.find_gouge_by_id(gouge_id)
