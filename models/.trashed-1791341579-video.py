from extensions import db


class TeachingScenario(db.Model):
    __tablename__ = "teachingscenario"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    subject = db.Column(
        db.String(100),
        nullable=False
    )

    level = db.Column(
        db.String(50),
        nullable=False
    )

    prompt_text = db.Column(
        db.Text,
        nullable=False
    )

    generated_by = db.Column(
        db.Enum("ai","bank"),
        nullable=False
    )

    video_submissions = db.relationship(
        "VideoSubmission",
        back_populates="scenario"
    )


class VideoSubmission(db.Model):
    __tablename__ = "videosubmission"

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

    scenario_id = db.Column(
        db.Integer,
        db.ForeignKey("teachingscenario.id"),
        nullable=False,
        index=True
    )

    video_url = db.Column(
        db.String(255),
        nullable=False
    )

    uploaded_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        nullable=False
    )

    status = db.Column(
        db.Enum(
            "pending",
            "uploaded",
            "ai_reviewed",
            "human_review",
            "completed",
            "failed"
        ),
        default="uploaded"
    )

    teacher = db.relationship(
        "Teacher",
        back_populates="video_submissions"
    )

    scenario = db.relationship(
        "TeachingScenario",
        back_populates="video_submissions"
    )

    reviews = db.relationship(
        "Review",
        back_populates="video",
        cascade="all, delete-orphan"
    )

    assignments = db.relationship(
        "ReviewAssignment",
        back_populates="video",
        cascade="all, delete-orphan"
    )