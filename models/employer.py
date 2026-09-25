from extensions import db
from models.user import User


class Employer(User):
    __tablename__ = "employer"

    id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    # FIX: removed duplicate `type` column and `polymorphic_on` — those belong on User only
    __mapper_args__ = {
        "polymorphic_identity": "employer",
    }

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


class Organization(Employer):
    __tablename__ = "organization"

    id = db.Column(db.Integer, db.ForeignKey("employer.id"), primary_key=True)
    org_name = db.Column(db.String(150), nullable=False)
    cac_number = db.Column(db.String(50))
    location = db.Column(db.String(255))

    __mapper_args__ = {
        "polymorphic_identity": "organization",
    }


class Parent(Employer):
    __tablename__ = "parent"

    id = db.Column(db.Integer, db.ForeignKey("employer.id"), primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    id_card = db.Column(db.String(255))
    picture_upload = db.Column(db.String(255))

    __mapper_args__ = {
        "polymorphic_identity": "parent",
    }


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

    position = db.Column(db.String(100), nullable=False)
    hired_at = db.Column(db.Date, nullable=False)
    ended_at = db.Column(db.Date)

    status = db.Column(
        db.Enum("active", "suspended", "terminated", name="recruitment_status"),
        nullable=False,
        default="active"
    )

    employer = db.relationship(
        "Employer",
        back_populates="recruitment_history"
    )

    # FIX: was missing — Teacher declares back_populates="teacher" on its side
    teacher = db.relationship(
        "Teacher",
        back_populates="recruitment_history"
    )
