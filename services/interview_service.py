from datetime import datetime

from models.interview import InterviewRequest
from models.teacher import Teacher
from models.employer import Employer
from extensions import db
from errors.exceptions import BadRequestError, ConflictError, ForbiddenError, NotFoundError


def create_request(employer_id, teacher_id, contact_method):
    # Validate contact method
    if contact_method not in ("whatsapp", "email"):
        raise BadRequestError("Invalid contact method")

    # Teacher must exist
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        raise NotFoundError("Teacher not found")

    # Prevent duplicate active requests
    existing = (
        InterviewRequest.query
        .filter(
            InterviewRequest.employer_id == employer_id,
            InterviewRequest.teacher_id == teacher_id,
            InterviewRequest.status.in_(["pending", "accepted"])
        )
        .first()
    )

    if existing:
        raise ConflictError("Interview request already exists")

    request = InterviewRequest(
        employer_id=employer_id,
        teacher_id=teacher_id,
        contact_method=contact_method,
        status="pending",
    )

    db.session.add(request)
    db.session.commit()

    # Email provider is TBD.
    # Notification integration should be added through an API adapter
    # once the provider is selected.

    return request


def respond_to_request(teacher_id, request_id, action):
    if action not in ("accepted", "rejected"):
        raise BadRequestError("Invalid action")

    request = InterviewRequest.query.get(request_id)

    if not request:
        raise NotFoundError("Interview request not found")

    # Ownership
    if request.teacher_id != teacher_id:
        raise ForbiddenError("Forbidden")

    if request.status != "pending":
        raise BadRequestError("Request can only be answered while pending")

    request.status = action
    request.updated_at = datetime.utcnow()

    db.session.commit()

    return request


def get_requests(user_id, role, status_filter=None):
    query = InterviewRequest.query

    if role == "teacher":
        query = query.filter(
            InterviewRequest.teacher_id == user_id
        )

    elif role in ("organization", "parent", "employer"):
        query = query.filter(
            InterviewRequest.employer_id == user_id
        )

    else:
        raise BadRequestError("Invalid role")

    if status_filter is not None:
        if status_filter not in ("pending", "accepted", "rejected"):
            raise BadRequestError("Invalid status filter")

        query = query.filter(
            InterviewRequest.status == status_filter
        )

    return query.all()


