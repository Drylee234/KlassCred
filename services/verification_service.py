from models.user import User
from models.teacher import Teacher
from models.employer import Organization, Parent
from extensions import db
from errors.exceptions import BadRequestError, NotFoundError


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

    # Cencori verification integration is not implemented yet.
    pass

    # Expected normalized result from the Cencori adapter:
    # {
    #     "valid": True/False,
    #     "reason": ...
    # }

    if not result["valid"]:
        raise BadRequestError(result.get("reason", "Identity verification failed"))

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

    # Cencori verification integration is not implemented yet.
    pass

    # Expected normalized result from the Cencori adapter:
    # {
    #     "valid": True/False,
    #     "reason": ...
    # }

    if not result["valid"]:
        raise BadRequestError(
            result.get("reason", "Organization verification failed")
        )

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

    # Cencori verification integration is not implemented yet.
    pass

    # Expected normalized result from the Cencori adapter:
    # {
    #     "valid": True/False,
    #     "reason": ...
    # }

    if not result["valid"]:
        raise BadRequestError(
            result.get("reason", "Parent verification failed")
        )

    user = User.query.get(employer_id)

    if not user:
        raise NotFoundError("User not found")

    user.id_verified = True

    db.session.commit()

    return user

def _verification_not_available():
    raise BadRequestError(
        "Identity verification is not configured yet. "
        "The Cencori verification adapter must be implemented "
        "before an identity can be marked as verified."
    )


def verify_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)

    if not teacher:
        raise NotFoundError("Teacher not found")

    if not teacher.profile_complete:
        raise BadRequestError(
            "Profile must be complete before verification"
        )

    if not teacher.references:
        raise BadRequestError(
            "At least one reference is required"
        )

    if not teacher.documents:
        raise BadRequestError(
            "Identity documents are required"
        )

    _verification_not_available()


def verify_organization(employer_id):
    organization = Organization.query.get(employer_id)

    if not organization:
        raise NotFoundError("Organization not found")

    if not organization.cac_number:
        raise BadRequestError(
            "CAC number is required"
        )

    _verification_not_available()


def verify_parent(employer_id):
    parent = Parent.query.get(employer_id)

    if not parent:
        raise NotFoundError("Parent not found")

    if not parent.id_card:
        raise BadRequestError(
            "ID card is required"
        )

    _verification_not_available()