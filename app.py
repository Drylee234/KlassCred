from flask import Flask
from extensions import db, migrate, init_cloudinary
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    init_cloudinary(app)

    import models

    @app.get("/")
    def health():
        return {"status": "ok"}

    return app
    
app = create_app()

