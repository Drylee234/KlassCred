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

    from routes.auth import bp as auth_bp
    from routes.teacher import bp as teacher_bp
    from routes.employer import bp as employer_bp
    from routes.reviewer import bp as reviewer_bp
    from routes.verification import bp as verification_bp
    from routes.webhooks import bp as webhooks_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(employer_bp)
    app.register_blueprint(reviewer_bp)
    app.register_blueprint(verification_bp)
    app.register_blueprint(webhooks_bp)

    from errors.handlers import register_error_handlers
    register_error_handlers(app)

    @app.get("/")
    def health():
        return {"status": "ok"}

    @app.get("/test")
    def test_ui():
        return send_from_directory("static", "klasscred_test_ui.html")


    return app


app = create_app()
