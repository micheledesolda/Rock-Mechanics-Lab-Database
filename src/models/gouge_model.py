# src/models/gouge_model.py
import os
from mongoengine import StringField, EmbeddedDocument

gouges_collection_name = os.getenv("COLLECTION_GOUGES") or "Gouges"

class GougeModel(EmbeddedDocument):
    gouge_id = StringField(primary_key=True)
    thickness_mm = StringField(required=True)

    meta = {'collection': gouges_collection_name}
