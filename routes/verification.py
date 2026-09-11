from flask import Blueprint, g

from schemas.user import UserSchema

from services import verification_service

from utils.auth_utils import require_role

bp = Blueprint("verification", __name__, url_prefix="/verify")


@bp.post("/teacher/<int:teacher_id>")
@require_role("reviewer")
def verify_teacher(teacher_id):
    user = verification_service.verify_teacher(
        teacher_id=teacher_id,
    )

    return UserSchema().dump(user), 200


@bp.post("/organization/<int:employer_id>")
@require_role("reviewer")
def verify_organization(employer_id):
    user = verification_service.verify_organization(
        employer_id=employer_id,
    )

    return UserSchema().dump(user), 200


@bp.post("/parent/<int:employer_id>")
@require_role("reviewer")
def verify_parent(employer_id):
    user = verification_service.verify_parent(
        employer_id=employer_id,
    )

    return UserSchema().dump(user), 200