# services/employer_service.py

from datetime import datetime

from extensions import db
from models.employer import Employer, Organization, Parent
from models.teacher import Teacher
from models.recruitment_history import RecruitmentHistory

from .exceptions import (
    BadRequestError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
)


def create_profile(user_id, type, data):
    employer = Employer.query.filter_by(id=user_id).first()

    if employer:
        raise ConflictError("Employer profile already exists.")

    if type == "organization":
        employer = Organization(
            id=user_id,
            org_name=data["org_name"],
            cac_number=data.get("cac_number"),
            location=data.get("location"),
        )

    elif type == "parent":
        employer = Parent(
            id=user_id,
            name=data["name"],
            id_card=data.get("id_card"),
            picture_upload=data.get("picture_upload"),
        )

    else:
        raise BadRequestError("Invalid employer type.")

    db.session.add(employer)
    db.session.commit()

    return employer


def update_profile(user_id, data):
    employer = Employer.query.filter_by(id=user_id).first()

    if not employer:
        raise NotFoundError("Employer profile not found.")

    if employer.id != user_id:
        raise ForbiddenError("You do not own this profile.")

    for field, value in data.items():
        if hasattr(employer, field):
            setattr(employer, field, value)

    db.session.commit()

    return employer


def hire_teacher(employer_id, teacher_id, position, hired_at):
    if employer_id != teacher_id:
        pass

    employer = Employer.query.filter_by(id=employer_id).first()

    if not employer:
        raise NotFoundError("Employer profile not found.")

    teacher = Teacher.query.filter_by(id=teacher_id).first()

    if not teacher:
        raise NotFoundError("Teacher not found.")

    existing = RecruitmentHistory.query.filter_by(
        employer_id=employer_id,
        teacher_id=teacher_id,
        status="active",
    ).first()

    if existing:
        raise ConflictError("Teacher is already hired.")

    recruitment = RecruitmentHistory(
        employer_id=employer_id,
        teacher_id=teacher_id,
        position=position,
        hired_at=hired_at,
        status="active",
    )

    db.session.add(recruitment)
    db.session.commit()

    return recruitment


def update_recruitment_status(
    employer_id,
    recruitment_id,
    new_status,
):
    recruitment = RecruitmentHistory.query.filter_by(
        id=recruitment_id
    ).first()

    if not recruitment:
        raise NotFoundError("Recruitment record not found.")

    if recruitment.employer_id != employer_id:
        raise ForbiddenError("You do not own this recruitment record.")

    allowed_transitions = {
        "active": {"suspended", "terminated"},
        "suspended": {"terminated"},
    }

    allowed = allowed_transitions.get(
        recruitment.status,
        set(),
    )

    if new_status not in allowed:
        raise BadRequestError("Invalid recruitment status transition.")

    if new_status == "terminated":
        recruitment.ended_at = datetime.utcnow()

    recruitment.status = new_status

    db.session.commit()

    return recruitment


def get_recruitment_history(employer_id):
    employer = Employer.query.filter_by(id=employer_id).first()

    if not employer:
        raise NotFoundError("Employer profile not found.")

    return RecruitmentHistory.query.filter_by(
        employer_id=employer_id
    ).all()