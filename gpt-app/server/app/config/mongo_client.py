from pymongo import MongoClient
from fastapi import FastAPI
from contextlib import asynccontextmanager

import config.settings as settings

# Lifespan event handler to manage MongoDB connection
@asynccontextmanager
async def lifespan(app: FastAPI):
    client = MongoClient(settings.db_uri)
    client.admin.command('ping')
    app.state.mongo_client = client
    print("Connected to MongoDB")
    try:
        yield
    finally:
        client.close()
        print("MongoDB connection closed")
