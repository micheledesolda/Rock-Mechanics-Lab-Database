# src/models/experiment_model.py
import os
from mongoengine import Document, StringField, ListField, DictField, EmbeddedDocumentField
from models.block_model import BlockModel
from models.gouge_model import GougeModel

experiments_collection_name = os.getenv("COLLECTION_EXPERIMENTS") or "Experiments"

class ExperimentModel(Document):
    experiment_id = StringField(primary_key=True)
    experiment_type = StringField(required=False)
    gouges = ListField(EmbeddedDocumentField(GougeModel), default=[])
    core_sample_id = StringField(required=False)
    blocks = ListField(EmbeddedDocumentField(BlockModel), default=[])
    centralized_measurements = ListField(DictField(default={}))
    additional_measurements = ListField(DictField(default={}))

    meta = {'collection': experiments_collection_name}
