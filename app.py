from flask import Flask, abort, redirect, render_template, url_for
from jinja2 import TemplateNotFound
from extensions import db, migrate, init_byteship
from config import Config

ROLES = ("teacher", "employer", "reviewer")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    init_byteship(app)

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

    # ── UI pages ─────────────────────────────────────────────────────────
    # Templates: templates/   Assets: static/ (css/, js/)
    # Everything lives under /app so it can't clash with the API prefixes
    # (/reviewer/*, /teachers/*, /employers/*, /auth/*, /verify/*).
    #   /app/                  login + register
    #   /app/<role>/           that role's dashboard (templates/<role>/index.html)
    #   /app/<role>/<page>     any other page   (templates/<role>/<page>.html)
    @app.get("/app/")
    def login_page():
        return render_template("index.html")

    @app.get("/app/<role>/", defaults={"page": "index"})
    @app.get("/app/<role>/<page>")
    def portal_page(role, page):
        if role not in ROLES or page.startswith("_"):   # "_" = layouts/partials
            abort(404)
        name = f"{role}/{page}.html"
        try:
            return render_template(name, role=role, page=page)
        except TemplateNotFound as e:
            if e.name != name:      # a missing include/extends is a real bug — don't hide it as a 404
                raise
            abort(404)

    @app.get("/test")               # old entry point — keep existing links working
    def legacy_test_ui():
        return redirect(url_for("login_page"))

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
