from extensions import db
from models.user import User
from sqlalchemy import CheckConstraint


class Teacher(User):
    __tablename__ = "teacher"

    id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)  # FIX: was missing

    __mapper_args__ = {
        "polymorphic_identity": "teacher",
    }

    full_name = db.Column(
        db.String(100),
        nullable=False
    )

    subjects = db.Column(
        db.JSON,
        nullable=False
    )

    experience_years = db.Column(
        db.Integer,
        nullable=False
    )

    profile_complete = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )
    
    documents = db.Column(db.JSON)

    work_history = db.relationship(
        "WorkHistory",
        back_populates="teacher",
        cascade="all, delete-orphan"
    )

    references = db.relationship(
        "Reference",
        back_populates="teacher",
        cascade="all, delete-orphan"
    )

    exam_attempts = db.relationship(
        "ExamAttempt",
        back_populates="teacher",
        cascade="all, delete-orphan"
    )

    video_submissions = db.relationship(
        "VideoSubmission",
        back_populates="teacher",
        cascade="all, delete-orphan"
    )

    rating = db.relationship(
        "Rating",
        back_populates="teacher",
        uselist=False,
        cascade="all, delete-orphan"
    )

    interview_requests = db.relationship(
        "InterviewRequest",
        back_populates="teacher",
        cascade="all, delete-orphan"
    )

    recruitment_history = db.relationship(
        "RecruitmentHistory",
        back_populates="teacher"
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

    full_name = db.Column(
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
        db.String(120),
        nullable=False
    )

    phone = db.Column(
        db.String(30),
        nullable=False
    )

    relationship_type = db.Column(
        db.String(100),
        nullable=False
    )

    teacher = db.relationship(
        "Teacher",
        back_populates="references"
    )


class WorkHistory(db.Model):
    __tablename__ = "work_history"

    __table_args__ = (
        CheckConstraint(
            'end_date IS NULL OR end_date >= start_date',
            name='check_end_date_after_start_date'
        ),
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
        nullable=False
    )

    end_date = db.Column(
        db.Date
    )

    teacher = db.relationship(
        "Teacher",
        back_populates="work_history"
    )
