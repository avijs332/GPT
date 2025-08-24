import io
from config import settings
from pymongo import MongoClient
import gridfs
from bson import ObjectId
from typing import BinaryIO

client = MongoClient(settings.db_uri)
db = client[settings.db_name]
fs = gridfs.GridFS(db)

def fetch_model(doc_id):
    with open(f'./loaded_models/actor_{doc_id}.keras', 'wb') as fileObject:
        fileObject.write(fs.get(ObjectId(doc_id)).read())

def save_model_to_db(file_obj: BinaryIO, filename: str):
    """Save a model file-like object to MongoDB GridFS."""
    return fs.put(file_obj, filename=filename)
