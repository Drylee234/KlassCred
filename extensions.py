from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt

from api import byteship

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()


def init_byteship(app):
    byteship.init_client(
        api_key=app.config["BYTESHIP_API_KEY"],
        webhook_secret=app.config["BYTESHIP_WEBHOOK_SECRET"],
    )