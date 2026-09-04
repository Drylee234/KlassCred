from flask_login import UserMixin

from extensions import db


class User(UserMixin, db.Model):
    __abstract__ = True

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now()
    )

    def get_id(self):
        return f"{self.__tablename__}:{self.id}"