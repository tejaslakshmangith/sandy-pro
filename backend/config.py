"""Application configuration."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_PRO_MODEL = "gemini-2.5-pro"
    GEMINI_FLASH_MODEL = "gemini-2.5-flash"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB upload limit
    UPLOAD_FOLDER = "uploads"
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp"}
    ML_MODEL_PATH = "ml_models/classifier.pkl"
    DATASET_PATH = "data/minerals_dataset.csv"
    SECRET_KEY = os.getenv("SECRET_KEY", "sandy-pro-mining-secret")
