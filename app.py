from flask import Flask,send_from_directory,abort
from extensions import db, migrate, init_cloudinary
from config import Config
import os



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
        return send_from_directory("static", "index.html")

    @app.route('/<page_name>.html')
    def serve_html(page_name):
        file_path = os.path.join(app.static_folder, f'{page_name}.html')
        if not os.path.isfile(file_path):
            abort(404)
        return send_from_directory(app.static_folder, f'{page_name}.html')

    @app.get("/diag/gemini-reachable")
    def diag_gemini():
        import requests, time
        t0 = time.time()
        try:
            r = requests.get("https://generativelanguage.googleapis.com", timeout=8)
            return {"reached": True, "status": r.status_code, "elapsed": time.time() - t0}
        except requests.RequestException as e:
            return {"reached": False, "error": str(e), "elapsed": time.time() - t0}

    @app.get("/diag/gemini-call")
    def diag_gemini_call():
        import time
        t0 = time.time()
        try:
            from api import gemini as ai_provider
            result = ai_provider.generate_scenario(subject="Mathematics", level="beginner")
            return {"ok": True, "elapsed": time.time() - t0, "result_preview": str(result)[:200]}
        except Exception as e:
            return {"ok": False, "elapsed": time.time() - t0, "error": type(e).__name__, "message": str(e)}


    return app


app = create_app()
