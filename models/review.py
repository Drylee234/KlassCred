from extensions import db


class ReviewAssignment(db.Model):
    __tablename__ = "review_assignment"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    video_id = db.Column(
        db.Integer,
        db.ForeignKey("videosubmission.id"),
        nullable=False,
        index=True
    )

    reviewer_id = db.Column(
        db.Integer,
        db.ForeignKey("reviewer.id"),
        nullable=False,
        index=True
    )

    # FIX: removed dead "pending" value — assignment is active the moment it's created
    status = db.Column(
        db.Enum("assigned", "in_progress", "completed", "cancelled",
                name="assignment_status"),
        nullable=False,
        default="assigned"
    )

    assigned_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    completed_at = db.Column(
        db.DateTime
    )

    video = db.relationship(
        "VideoSubmission",
        back_populates="assignments"
    )

    reviewer = db.relationship(
        "Reviewer",
        back_populates="review_assignments"
    )


class Review(db.Model):
    __tablename__ = "review"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    video_id = db.Column(
        db.Integer,
        db.ForeignKey("videosubmission.id"),
        nullable=False,
        index=True
    )

    reviewer_id = db.Column(
        db.Integer,
        db.ForeignKey("reviewer.id"),
        nullable=True,
        index=True
    )

    reviewer_type = db.Column(db.Enum("ai", "human", name="review_reviewer_type"), nullable=False)


    score = db.Column(
        db.Float
    )

    notes = db.Column(
        db.Text
    )

    flagged = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    flag_reason = db.Column(
        db.Text
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    video = db.relationship(
        "VideoSubmission",
        back_populates="reviews"
    )

    reviewer = db.relationship(
        "Reviewer",
        back_populates="reviews"
    )
