from app import app
from extensions import db

with app.app_context():
    db.session.execute(db.text("DROP TABLE IF EXISTS alembic_version"))
    db.session.commit()
    print("done")
