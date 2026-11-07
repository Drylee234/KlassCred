import os
from datetime import timedelta


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CELERY_BROKER_URL =  os.environ.get("REDIS_URL","")
    
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    SESSION_COOKIE_SECURE = os.environ.get(
        "SESSION_COOKIE_SECURE", "false"
    ).casefold() == "true"

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret")
    JWT_EXPIRY = timedelta(minutes=7)
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI", "")
    ADMIN_EMAILS = tuple(
        email.strip().casefold()
        for email in os.environ.get("ADMIN_EMAILS", "").split(",")
        if email.strip()
    )
    CORS_ALLOWED_ORIGINS = tuple(
        origin.strip().rstrip("/")
        for origin in os.environ.get(
            "CORS_ALLOWED_ORIGINS",
            "https://klasscred-pr-20.onrender.com",
        ).split(",")
        if origin.strip()
    )

    CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET", "")
