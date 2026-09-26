from flask import Blueprint, request, g

from schemas.review import ReviewAssignmentSchema, HumanReviewSubmitSchema, ReviewSchema
from schemas.rating import RatingSchema
from schemas.reviewer import ReviewerSchema

from services import (
    reviewer_service,
    review_service,
    rating_service,
)

from utils.auth_utils import require_role

bp = Blueprint("reviewer", __name__, url_prefix="/reviewer")



@bp.get("/profile")
@require_role("reviewer")
def get_profile():
    reviewer = reviewer_service.get_profile(user_id=g.current_user.id)
    return ReviewerSchema().dump(reviewer), 200
@bp.get("/verification/pending")
@require_role("reviewer")
def get_pending_verification():
    verification_type = request.args.get("type", "teacher").lower()

    if verification_type == "teacher":
        pending = Teacher.query.filter_by(id_verified=False).all()
        return TeacherSchema(many=True).dump(pending), 200

    if verification_type == "organization":
        pending = Organization.query.filter_by(id_verified=False).all()
        return OrganizationSchema(many=True).dump(pending), 200

    if verification_type == "parent":
        pending = Parent.query.filter_by(id_verified=False).all()
        return ParentSchema(many=True).dump(pending), 200

    raise BadRequestError(
        "Invalid verification type. "
        "Expected teacher, organization, or parent."
    )
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