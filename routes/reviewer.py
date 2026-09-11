from flask import Blueprint, request, g

from schemas.review import ReviewAssignmentSchema, HumanReviewSubmitSchema, ReviewSchema
from schemas.rating import RatingSchema

from services import (
    reviewer_service,
    review_service,
    rating_service,
)

from utils.auth_utils import require_role

bp = Blueprint("reviewer", __name__, url_prefix="/reviewer")


# ─── Assignments ────────────────────────────────────────────

@bp.get("/assignments")
@require_role("reviewer")
def get_assignments():
    assignments = (
        review_service.get_assignments_for_reviewer(
            reviewer_id=g.current_user.id,
        )
    )

    return ReviewAssignmentSchema(many=True).dump(assignments), 200


@bp.post("/assignments/<int:assignment_id>/review")
@require_role("reviewer")
def submit_review(assignment_id):
    data = HumanReviewSubmitSchema().load(request.get_json())

    result = review_service.submit_human_review(
        reviewer_id=g.current_user.id,
        assignment_id=assignment_id,
        data=data,
    )

    return ReviewSchema().dump(result), 201


# ─── Rating Override ─────────────────────────────────────────

@bp.post("/ratings/<int:teacher_id>/override")
@require_role("reviewer")
def override_rating(teacher_id):
    data = request.get_json()

    rating = rating_service.override_rating(
        teacher_id=teacher_id,
        composite=data["composite"],
        reason=data["reason"],
    )

    return RatingSchema().dump(rating), 200