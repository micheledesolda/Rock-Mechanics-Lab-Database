# src/models/block.py
import os
from mongoengine import Document, StringField, FloatField, DictField, ListField, EmbeddedDocument, EmbeddedDocumentField
from models.sensor_model import SensorModel

blocks_collection_name = os.getenv("COLLECTION_BLOCKS") or "Blocks"

class BlockModel(EmbeddedDocument):
    block_id = StringField(primary_key=True)
    material = StringField(required=True)
    dimensions = DictField(required=True)
    sensor_rail_width = FloatField(required=True)
    sensors = ListField(EmbeddedDocumentField(SensorModel))
    position = StringField(required=False)
    meta = {'collection': blocks_collection_name}