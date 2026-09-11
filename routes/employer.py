from flask import Blueprint, request, g

from schemas.employer import (
    OrganizationSchema,
    ParentSchema,
    RecruitmentHistorySchema,
)
from schemas.teacher import TeacherSchema
from schemas.interview import InterviewRequestSchema

from services import (
    employer_service,
    search_service,
    interview_service,
)

from utils.auth_utils import require_role

bp = Blueprint("employer", __name__, url_prefix="/employers")


# ─── Profile ────────────────────────────────────────────────

@bp.post("/profile")
@require_role("organization", "parent")
def create_profile():
    data = request.get_json()
    user = g.current_user

    employer = employer_service.create_profile(
        user_id=user.id,
        type=user.type,
        data=data,
    )

    schema = OrganizationSchema() if user.type == "organization" else ParentSchema()

    return schema.dump(employer), 201


@bp.put("/profile")
@require_role("organization", "parent")
def update_profile():
    data = request.get_json()

    employer = employer_service.update_profile(
        user_id=g.current_user.id,
        data=data,
    )

    schema = OrganizationSchema() if g.current_user.type == "organization" else ParentSchema()

    return schema.dump(employer), 200


# ─── Search ─────────────────────────────────────────────────

@bp.get("/search")
@require_role("organization", "parent")
def search_teachers():
    subject = request.args.get("subject")
    min_rating = request.args.get("min_rating", type=float)
    verified_only = request.args.get("verified_only", default=True, type=lambda v: v.lower() == "true")

    teachers = search_service.search_teachers(
        subject=subject,
        min_rating=min_rating,
        verified_only=verified_only,
    )

    return TeacherSchema(many=True).dump(teachers), 200


# ─── Recruitment ────────────────────────────────────────────

@bp.post("/hire")
@require_role("organization", "parent")
def hire_teacher():
    data = request.get_json()

    recruitment = employer_service.hire_teacher(
        employer_id=g.current_user.id,
        teacher_id=data["teacher_id"],
        position=data["position"],
        hired_at=data["hired_at"],
    )

    return RecruitmentHistorySchema().dump(recruitment), 201


@bp.put("/recruitment/<int:recruitment_id>")
@require_role("organization", "parent")
def update_recruitment_status(recruitment_id):
    data = request.get_json()

    recruitment = employer_service.update_recruitment_status(
        employer_id=g.current_user.id,
        recruitment_id=recruitment_id,
        new_status=data["status"],
    )

    return RecruitmentHistorySchema().dump(recruitment), 200


@bp.get("/recruitment")
@require_role("organization", "parent")
def get_recruitment_history():
    records = employer_service.get_recruitment_history(
        employer_id=g.current_user.id,
    )

    return RecruitmentHistorySchema(many=True).dump(records), 200


# ─── Interviews ─────────────────────────────────────────────

@bp.post("/interviews")
@require_role("organization", "parent")
def create_interview_request():
    data = request.get_json()

    result = interview_service.create_request(
        employer_id=g.current_user.id,
        teacher_id=data["teacher_id"],
        contact_method=data["contact_method"],
    )

    return InterviewRequestSchema().dump(result), 201


@bp.get("/interviews")
@require_role("organization", "parent")
def get_interview_requests():
    status_filter = request.args.get("status")

    requests = interview_service.get_requests(
        user_id=g.current_user.id,
        role=g.current_user.type,
        status_filter=status_filter,
    )

    return InterviewRequestSchema(many=True).dump(requests), 200