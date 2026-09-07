from extensions import db
from models.user import User


class Reviewer(User):
    __tablename__ = "reviewer"
    
    __mapper_args__ = {
        "polymorphic_identity": "reviewer",
    }

    id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)

    full_name = db.Column(
        db.String(255),
        nullable=False
    )
    
    review_assignments = db.relationship(
        "ReviewAssignment",
        back_populates="reviewer",
        cascade="all, delete-orphan"
    )

    reviews = db.relationship( 
        "Review",
        back_populates="reviewer"
    )