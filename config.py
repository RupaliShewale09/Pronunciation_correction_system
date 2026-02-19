import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    # 1. App Security
    SECRET_KEY = os.environ.get("SECRET_KEY")

    # 2. Database
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 3. Authentication
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24) 

    # 4. Gemini API
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

