from flask_login import UserMixin

from extensions import db


class User(UserMixin, db.Model):
    
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    
    type = db.Column(db.String(50))

    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "employer",
    }
    

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

    id_verified = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )
    
    def get_id(self):
        return f"{self.__tablename__}:{self.id}"