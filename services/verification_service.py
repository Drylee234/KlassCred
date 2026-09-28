from models.user import User
from models.teacher import Teacher
from models.employer import Organization, Parent
from extensions import db
from errors.exceptions import BadRequestError, NotFoundError

# Note on design: these functions are only reachable through
# @require_role("reviewer") routes (see routes/verification.py). A human
# reviewer has already inspected the person's documents before calling
# them, so the reviewer's action IS the verification. An earlier draft
# tried to call a Cencori "identity check" adapter that was never built,
# which made every call crash on an undefined variable. It was removed
# rather than faked: an AI cannot reliably confirm an ID is authentic,
# and we don't want to imply it did.


def verify_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)

    if not teacher:
        raise NotFoundError("Teacher not found")

    if not teacher.profile_complete:
        raise BadRequestError("Profile must be complete before verification")

    if not teacher.references:
        raise BadRequestError("At least one reference is required")

    if not teacher.documents:
        raise BadRequestError("Identity documents are required")

    user = User.query.get(teacher_id)

    if not user:
        raise NotFoundError("User not found")

    user.id_verified = True

    db.session.commit()

    return user


def verify_organization(employer_id):
    organization = Organization.query.get(employer_id)

    if not organization:
        raise NotFoundError("Organization not found")

    if not organization.cac_number:
        raise BadRequestError("CAC number is required")

    user = User.query.get(employer_id)

    if not user:
        raise NotFoundError("User not found")

    user.id_verified = True

    db.session.commit()

    return user


def verify_parent(employer_id):
    parent = Parent.query.get(employer_id)

    if not parent:
        raise NotFoundError("Parent not found")

    if not parent.id_card:
        raise BadRequestError("ID card is required")

    user = User.query.get(employer_id)

    if not user:
        raise NotFoundError("User not found")

    user.id_verified = True

    db.session.commit()

    return user
