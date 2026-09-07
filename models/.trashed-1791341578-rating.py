from extensions import db


class Rating(db.Model):
    __tablename__ = "rating"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey("teacher.id"),
        nullable=False,
        unique=True,
        index=True
    )

    exam_score = db.Column(
        db.Float
    )

    video_score = db.Column(
        db.Float
    )

    reference_score = db.Column(
        db.Float
    )

    profile_score = db.Column(
        db.Float
    )

    composite = db.Column(
        db.Float,
        index=True
    )

    overridden = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    override_reason = db.Column(
        db.Text
    )

    breakdown = db.Column(
        db.JSON
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )

    teacher = db.relationship(
        "Teacher",
        back_populates="rating"
    )