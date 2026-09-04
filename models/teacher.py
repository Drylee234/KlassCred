from extensions import db
from models.user import User


class Teacher(User):
    __tablename__ = "teacher"

    full_name = db.Column(
        db.String(100),
        nullable=False
    )

    subjects = db.Column(
        db.JSON
    )

    experience_years = db.Column(
        db.Integer
    )

    id_verified = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    profile_complete = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    # Teacher → WorkHistory
    work_history = db.relationship(
        "WorkHistory",
        back_populates="teacher",
        cascade="all, delete-orphan"
    )

    # Teacher → Reference
    references = db.relationship(
        "Reference",
        back_populates="teacher",
        cascade="all, delete-orphan"
    )

    # Teacher → ExamAttempt
    exam_attempts = db.relationship(
        "ExamAttempt",
        back_populates="teacher",
        cascade="all, delete-orphan"
    )

    # Teacher → VideoSubmission
    video_submissions = db.relationship(
        "VideoSubmission",
        back_populates="teacher",
        cascade="all, delete-orphan"
    )

    # Teacher → Rating
    rating = db.relationship(
        "Rating",
        back_populates="teacher",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # Teacher → InterviewRequest
    interview_requests = db.relationship(
        "InterviewRequest",
        back_populates="teacher",
        cascade="all, delete-orphan"
    )