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
    
    recruitment_history = db.relationship(
        "RecruitmentHistory",
        back_populates="employer",
        cascade="all, delete-orphan"
    )
    
    
class RecruitmentHistory(db.Model):
    __tablename__ = "recruitment_history"

    id = db.Column(db.Integer, primary_key=True)

    employer_id = db.Column(
        db.Integer,
        db.ForeignKey("employer.id"),
        nullable=False,
        index=True
    )

    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey("teacher.id"),
        nullable=False,
        index=True
    )

    position = db.Column(
        db.String(100),
        nullable=False
    )

    hired_at = db.Column(
        db.Date,
        nullable=False
    )

    ended_at = db.Column(
        db.Date
    )

    status = db.Column(
        db.Enum("active","suspended","terminated"),
        nullable=False,
        default="active"
    )

    employer = db.relationship(
        "Employer",
        back_populates="recruitment_history"
    )