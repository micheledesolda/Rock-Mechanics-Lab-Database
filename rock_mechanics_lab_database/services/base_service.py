# rock_mechanics_lab_database/services/base_service.py
from typing import Any, Dict
from rock_mechanics_lab_database.daos.base_dao import BaseDao

class BaseService:
    def __init__(self, dao: BaseDao):
        self.dao = dao

    def create(self, document: Dict[str, Any]) -> str:
        return self.dao.create(self.dao.collection_name, document)

    def read(self, query: Dict[str, Any]) -> Dict[str, Any]:
        return self.dao.read(self.dao.collection_name, query)

    def update(self, query: Dict[str, Any], update_values: Dict[str, Any]) -> bool:
        return self.dao.update(self.dao.collection_name, query, update_values)

    def delete(self, query: Dict[str, Any]) -> bool:
        return self.dao.delete(self.dao.collection_name, query)
