from extensions import db
from models.user import User


class Reviewer(User):
    __tablename__ = "reviewer"

    review_assignments = db.relationship(
        "ReviewAssignment",
        back_populates="reviewer",
        cascade="all, delete-orphan"
    )

    reviews = db.relationship(
        "Review",
        back_populates="reviewer"
    )