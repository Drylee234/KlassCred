from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import cloudinary

db = SQLAlchemy()
migrate = Migrate()


def init_cloudinary(app):
    cloudinary.config(
        cloud_name=app.config["CLOUDINARY_CLOUD_NAME"],
        api_key=app.config["CLOUDINARY_API_KEY"],
        api_secret=app.config["CLOUDINARY_API_SECRET"]
    )