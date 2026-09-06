from extensions import db
from models.user import User
from sqlalchemy import CheckConstraint


class Teacher(User):
    __tablename__ = "teacher"
    
    __mapper_args__ = {
        "polymorphic_identity": "teacher",
    }


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
    
    recruitment_history = db.relationship(
    "RecruitmentHistory",
    back_populates="teacher",
    cascade="all, delete-orphan"
)
    



class Reference(db.Model):
    __tablename__ = "reference"

    id = db.Column(db.Integer, primary_key=True)

    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey("teacher.id"),
        nullable=False,
        index=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    organization = db.Column(
        db.String(150)
    )

    role = db.Column(
        db.String(100)
    )

    email = db.Column(
        db.String(120)
    )

    phone = db.Column(
        db.String(30)
    )

    relationship_type = db.Column(
        db.String(100)
    )

    teacher = db.relationship(
        "Teacher",
        back_populates="references"
    )
    



class WorkHistory(db.Model):
    __tablename__ = "work_history"
    
    __table_args__ = (
        # Ensures end_date is on or after start_date if end_date is provided
        CheckConstraint('end_date IS NULL OR end_date >= start_date', name='check_end_date_after_start_date'),
    )

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey("teacher.id"),
        nullable=False,
        index=True
    )

    organization = db.Column(
        db.String(150),
        nullable=False
    )

    role = db.Column(
        db.String(100),
        nullable=False
    )

    start_date = db.Column(
        db.Date,
        nullable=False,
    )

    end_date = db.Column(
        db.Date
    )

    teacher = db.relationship(
        "Teacher",
        back_populates="work_history"
    )