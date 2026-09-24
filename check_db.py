from app import app
from extensions import db

with app.app_context():
    tables = db.session.execute(
        db.text("SELECT tablename FROM pg_tables WHERE schemaname='public'")
    ).fetchall()
    types = db.session.execute(
        db.text("SELECT typname FROM pg_type WHERE typtype='e'")
    ).fetchall()
    print("Tables:", tables)
    print("Enum types:", types)
