# services/teacher_service.py

from models.teacher import Teacher, WorkHistory, Reference
from extensions import db

from errors.exceptions import (
    BadRequestError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
)

def get_profile(user_id):
    teacher = Teacher.query.filter_by(id=user_id).first()
    if not teacher:
        raise NotFoundError("Teacher profile not found.")
    return teacher
    
def create_profile(user_id, data):
    teacher = Teacher.query.filter_by(id=user_id).first()

    if teacher:
        raise ConflictError("Teacher profile already exists.")

    teacher = Teacher(
        id=user_id,
        full_name=data["full_name"],
        subjects=data["subjects"],
        experience_years=data["experience_years"],
        profile_complete=False,
    )

    db.session.add(teacher)
    db.session.commit()

    return teacher


def update_profile(user_id, data):
    teacher = Teacher.query.filter_by(id=user_id).first()

    if not teacher:
        raise NotFoundError("Teacher profile not found.")

    allowed_fields = {
        "full_name",
        "subjects",
        "experience_years",
        "documents",
    }

    for field, value in data.items():
        if field in allowed_fields:
            setattr(teacher, field, value)

    _check_profile_complete(teacher)

    db.session.commit()

    return teacher


def _check_profile_complete(teacher):
    teacher.profile_complete = bool(
        teacher.full_name
        and teacher.subjects
        and len(teacher.subjects) > 0
        and teacher.experience_years is not None
        and len(teacher.work_history) > 0
        and len(teacher.references) > 0
    )


def add_work_history(user_id, data):
    teacher = Teacher.query.filter_by(id=user_id).first()

    if not teacher:
        raise NotFoundError("Teacher profile not found.")

    start_date = data["start_date"]
    end_date = data.get("end_date")

    if end_date is not None and end_date < start_date:
        raise BadRequestError(
            "End date cannot be earlier than start date."
        )

    record = WorkHistory(
        teacher_id=user_id,
        organization=data["organization"],
        role=data["role"],
        start_date=start_date,
        end_date=end_date,
    )

    db.session.add(record)
    db.session.commit()

    _check_profile_complete(teacher)
    db.session.commit()

    return record


def delete_work_history(user_id, work_history_id):
    record = WorkHistory.query.filter_by(
        id=work_history_id
    ).first()

    if not record:
        raise NotFoundError("Work history not found.")

    if record.teacher_id != user_id:
        raise ForbiddenError("You do not own this record.")

    teacher = Teacher.query.filter_by(id=user_id).first()

    db.session.delete(record)
    db.session.flush()

    if teacher:
        _check_profile_complete(teacher)

    db.session.commit()


def add_reference(user_id, data):
    teacher = Teacher.query.filter_by(id=user_id).first()

    if not teacher:
        raise NotFoundError("Teacher profile not found.")

    record = Reference(
        teacher_id=user_id,
        full_name=data["full_name"],
        organization=data.get("organization"),
        role=data.get("role"),
        email=data["email"],
        phone=data["phone"],
        relationship_type=data["relationship_type"],
    )

    db.session.add(record)
    db.session.flush()

    _check_profile_complete(teacher)

    db.session.commit()

    return record


def delete_reference(user_id, reference_id):
    record = Reference.query.filter_by(
        id=reference_id
    ).first()

    if not record:
        raise NotFoundError("Reference not found.")

    if record.teacher_id != user_id:
        raise ForbiddenError("You do not own this record.")

    teacher = Teacher.query.filter_by(id=user_id).first()

    db.session.delete(record)
    db.session.flush()

    if teacher:
        _check_profile_complete(teacher)

    db.session.commit()