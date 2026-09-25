from datetime import datetime

from extensions import db
from models.employer import Organization, Parent
from models.teacher import Teacher
from errors.exceptions import BadRequestError, ConflictError, NotFoundError

# Teacher verification is a human-reviewed application:
#   not_requested -> (apply) -> pending -> (reviewer) -> approved | rejected
#   rejected -> (re-apply) -> pending
# Approval sets User.id_verified, which employer search filters on.

_REQUIREMENT_LABELS = {
    "profile_complete": "a complete profile",
    "references": "at least one reference",
    "id_documents": "ID card front and back",
}


def _get_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)

    if not teacher:
        raise NotFoundError("Teacher not found")

    return teacher


def _requirements(teacher):
    docs = teacher.documents or {}

    return {
        "profile_complete": bool(teacher.profile_complete),
        "references": len(teacher.references) > 0,
        "id_documents": bool(docs.get("id_card_front") and docs.get("id_card_back")),
    }


# ─── Teacher side ───────────────────────────────────────────

def get_status(teacher_id):
    teacher = _get_teacher(teacher_id)
    requirements = _requirements(teacher)

    return {
        "status": teacher.verification_status,
        "rejection_reason": teacher.verification_rejection_reason,
        "requested_at": teacher.verification_requested_at,
        "requirements": requirements,
        "can_apply": (
            teacher.verification_status in ("not_requested", "rejected")
            and all(requirements.values())
        ),
    }


def apply(teacher_id):
    teacher = _get_teacher(teacher_id)

    if teacher.verification_status == "pending":
        raise ConflictError("Your verification application is already pending.")

    if teacher.verification_status == "approved":
        raise ConflictError("You are already verified.")

    missing = [
        _REQUIREMENT_LABELS[name]
        for name, ok in _requirements(teacher).items()
        if not ok
    ]

    if missing:
        raise BadRequestError("Before applying you need: " + ", ".join(missing) + ".")

    teacher.verification_status = "pending"
    teacher.verification_requested_at = datetime.utcnow()
    teacher.verification_rejection_reason = None

    db.session.commit()

    return get_status(teacher_id)


# ─── Reviewer side ──────────────────────────────────────────

def list_pending():
    return (
        Teacher.query
        .filter_by(verification_status="pending")
        .order_by(Teacher.verification_requested_at.asc())
        .all()
    )


def get_teacher_for_review(teacher_id):
    return _get_teacher(teacher_id)


def approve_teacher(teacher_id):
    teacher = _get_teacher(teacher_id)

    if teacher.verification_status != "pending":
        raise BadRequestError("Only pending applications can be approved.")

    teacher.verification_status = "approved"
    teacher.id_verified = True
    teacher.verification_rejection_reason = None

    db.session.commit()

    return teacher


def reject_teacher(teacher_id, reason):
    reason = (reason or "").strip()

    if not reason:
        raise BadRequestError("A rejection reason is required.")

    teacher = _get_teacher(teacher_id)

    if teacher.verification_status != "pending":
        raise BadRequestError("Only pending applications can be rejected.")

    teacher.verification_status = "rejected"
    teacher.id_verified = False
    teacher.verification_rejection_reason = reason

    db.session.commit()

    return teacher


def verify_teacher(teacher_id):
    """Legacy POST /verify/teacher/<id> entry point: same as reviewer approve."""
    return approve_teacher(teacher_id)


# ─── Organizations / parents (Cencori adapter still pending) ─

def _verification_not_available():
    raise BadRequestError(
        "Identity verification is not configured yet. "
        "The Cencori verification adapter must be implemented "
        "before an identity can be marked as verified."
    )


def verify_organization(employer_id):
    organization = Organization.query.get(employer_id)

    if not organization:
        raise NotFoundError("Organization not found")

    if not organization.cac_number:
        raise BadRequestError("CAC number is required")

    _verification_not_available()


def verify_parent(employer_id):
    parent = Parent.query.get(employer_id)

    if not parent:
        raise NotFoundError("Parent not found")

    if not parent.id_card:
        raise BadRequestError("ID card is required")

    _verification_not_available()