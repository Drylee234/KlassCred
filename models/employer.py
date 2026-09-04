from extensions import db
from models.user import User


class Employer(User):
    __tablename__ = "employer"

    org_name = db.Column(
        db.String(150),
        nullable=False
    )

    cac_number = db.Column(
        db.String(50)
    )

    verified = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    interview_requests = db.relationship(
        "InterviewRequest",
        back_populates="employer",
        cascade="all, delete-orphan"
    )