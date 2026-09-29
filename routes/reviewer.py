from flask import Blueprint, request, g

from models.teacher import Teacher
from models.employer import Organization, Parent

from schemas.review import ReviewAssignmentSchema, HumanReviewSubmitSchema, ReviewSchema
from schemas.rating import RatingSchema
from schemas.reviewer import ReviewerSchema
from schemas.teacher import TeacherSchema
from schemas.employer import OrganizationSchema, ParentSchema

from services import (
    reviewer_service,
    review_service,
    rating_service,
    teacher_service,
)

from errors.exceptions import BadRequestError, NotFoundError

from utils.auth_utils import require_role

bp = Blueprint("reviewer", __name__, url_prefix="/reviewer")



@bp.get("/profile")
@require_role("reviewer")
def get_profile():
    reviewer = reviewer_service.get_profile(user_id=g.current_user.id)
    return ReviewerSchema().dump(reviewer), 200


@bp.get("/teachers")
@require_role("reviewer")
def search_teachers():
    teachers = teacher_service.search_all_teachers(
        query=request.args.get("q"),
    )
    return TeacherSchema(many=True).dump(teachers), 200


@bp.get("/verification/teachers/<int:teacher_id>")
@require_role("reviewer")
def inspect_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        raise NotFoundError("Teacher not found")
    return TeacherSchema().dump(teacher), 200


@bp.post("/verification/teachers/<int:teacher_id>/approve")
@require_role("reviewer")
def approve_teacher(teacher_id):
    verification_service.verify_teacher(teacher_id)
    teacher = Teacher.query.get(teacher_id)
    return TeacherSchema().dump(teacher), 200


@bp.post("/verification/teachers/<int:teacher_id>/reject")
@require_role("reviewer")
def reject_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        raise NotFoundError("Teacher not found")

    data = request.get_json(silent=True) or {}
    reason = (data.get("reason") or "").strip()
    if not reason:
        raise BadRequestError("Rejection reason is required")

    # The current schema has no persisted verification-rejection state.
    # Keep the teacher unverified and return the reason to the reviewer.
    return {
        "status": "rejected",
        "teacher_id": teacher_id,
        "reason": reason,
    }, 200


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

@bp.get("/ratings/<int:teacher_id>")
@require_role("reviewer")
def get_teacher_rating(teacher_id):
    rating = rating_service.get_rating(teacher_id)
    return RatingSchema().dump(rating), 200


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