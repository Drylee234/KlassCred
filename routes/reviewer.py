from flask import Blueprint, request, g

from schemas.review import ReviewAssignmentSchema, HumanReviewSubmitSchema, ReviewSchema
from schemas.rating import RatingSchema
from schemas.reviewer import ReviewerSchema
from schemas.teacher import TeacherSchema, TeacherSummarySchema, VerificationRejectSchema

from services import (
    reviewer_service,
    review_service,
    rating_service,
    verification_service,
)

from utils.auth_utils import require_role

bp = Blueprint("reviewer", __name__, url_prefix="/reviewer")



@bp.get("/profile")
@require_role("reviewer")
def get_profile():
    reviewer = reviewer_service.get_profile(user_id=g.current_user.id)
    return ReviewerSchema().dump(reviewer), 200

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


# ─── Teacher search ─────────────────────────────────────────

@bp.get("/teachers")
@require_role("reviewer")
def search_teachers():
    teachers = reviewer_service.search_teachers(
        q=request.args.get("q"),
    )

    return TeacherSummarySchema(many=True).dump(teachers), 200


# ─── Teacher verification ───────────────────────────────────

@bp.get("/verification/pending")
@require_role("reviewer")
def get_pending_verifications():
    teachers = verification_service.list_pending()

    return TeacherSummarySchema(many=True).dump(teachers), 200


@bp.get("/verification/teachers/<int:teacher_id>")
@require_role("reviewer")
def inspect_teacher(teacher_id):
    teacher = verification_service.get_teacher_for_review(
        teacher_id=teacher_id,
    )

    return TeacherSchema().dump(teacher), 200


@bp.post("/verification/teachers/<int:teacher_id>/approve")
@require_role("reviewer")
def approve_teacher(teacher_id):
    teacher = verification_service.approve_teacher(
        teacher_id=teacher_id,
    )

    return TeacherSummarySchema().dump(teacher), 200


@bp.post("/verification/teachers/<int:teacher_id>/reject")
@require_role("reviewer")
def reject_teacher(teacher_id):
    data = VerificationRejectSchema().load(request.get_json())

    teacher = verification_service.reject_teacher(
        teacher_id=teacher_id,
        reason=data["reason"],
    )

    return TeacherSummarySchema().dump(teacher), 200


# ─── Rating lookup ──────────────────────────────────────────

@bp.get("/ratings/<int:teacher_id>")
@require_role("reviewer")
def get_rating(teacher_id):
    rating = rating_service.get_rating(teacher_id=teacher_id)

    return RatingSchema().dump(rating), 200