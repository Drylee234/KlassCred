import os
from datetime import timedelta


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret")
    JWT_EXPIRY = timedelta(days=7)

    BYTESHIP_API_KEY = os.environ.get("BYTESHIP_API_KEY", "")
    BYTESHIP_WEBHOOK_SECRET = os.environ.get("BYTESHIP_WEBHOOK_SECRET", "")