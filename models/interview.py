from extensions import db


class InterviewRequest(db.Model):
    __tablename__ = "interview_request"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

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

    contact_method = db.Column(
        db.String(20),
        nullable=False
    )

    status = db.Column(db.Enum("pending", "accepted", "rejected", name="interview_status"), nullable=False, default="pending")

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    updated_at = db.Column(
        db.DateTime
    )

    employer = db.relationship(
        "Employer",
        back_populates="interview_requests"
    )

    teacher = db.relationship(
        "Teacher",
        back_populates="interview_requests"
    )
