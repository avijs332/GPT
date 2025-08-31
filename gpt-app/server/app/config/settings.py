import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
from dotenv import load_dotenv

load_dotenv()

class Settings:
    db_uri: str = os.getenv("DB_URI", "mongodb://localhost:27017")
    db_name: str = os.getenv("DB_NAME", "sample_mflix")
    HOST: str = os.getenv("HOST", "localhost")
    PORT: int = int(os.getenv("PORT", 8000))
    environment: str = os.getenv("ENVIRONMENT", "development")
    secret_key: str = os.getenv("SECRET_KEY", "your_secret_key")
    models_route: str = os.getenv("MODELS_ROUTE", "./loaded_models")

settings = Settings()