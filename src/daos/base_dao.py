# src/daos/base_dao.py
import pymongo
from pymongo.collection import Collection
from typing import Tuple, Dict, Any, Optional
import os


# MongoDB connection details
url = os.getenv("MONGO_URL") or "mongodb://localhost:27017/"
db_name = os.getenv("DB_NAME") or "EPS"

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
