from models.user import User
from models.teacher import Teacher
from models.employer import Organization, Parent
from extensions import db


def verify_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)

    if not teacher:
        raise LookupError("Teacher not found")

    if not teacher.profile_complete:
        raise ValueError("Profile must be complete before verification")

    if not teacher.references:
        raise ValueError("At least one reference is required")

    if not teacher.documents:
        raise ValueError("Identity documents are required")

    # Cencori verification integration is not implemented yet.
    pass

    # Expected normalized result from the Cencori adapter:
    # {
    #     "valid": True/False,
    #     "reason": ...
    # }

    if not result["valid"]:
        raise ValueError(result.get("reason", "Identity verification failed"))

    user = User.query.get(teacher_id)

    if not user:
        raise LookupError("User not found")

    user.id_verified = True

    db.session.commit()

    return user


def verify_organization(employer_id):
    organization = Organization.query.get(employer_id)

    if not organization:
        raise LookupError("Organization not found")

    if not organization.cac_number:
        raise ValueError("CAC number is required")

    # Cencori verification integration is not implemented yet.
    pass

    # Expected normalized result from the Cencori adapter:
    # {
    #     "valid": True/False,
    #     "reason": ...
    # }

    if not result["valid"]:
        raise ValueError(
            result.get("reason", "Organization verification failed")
        )

    user = User.query.get(employer_id)

    if not user:
        raise LookupError("User not found")

    user.id_verified = True

    db.session.commit()

    return user


def verify_parent(employer_id):
    parent = Parent.query.get(employer_id)

    if not parent:
        raise LookupError("Parent not found")

    if not parent.id_card:
        raise ValueError("ID card is required")

    # Cencori verification integration is not implemented yet.
    pass

    # Expected normalized result from the Cencori adapter:
    # {
    #     "valid": True/False,
    #     "reason": ...
    # }

    if not result["valid"]:
        raise ValueError(
            result.get("reason", "Parent verification failed")
        )

    user = User.query.get(employer_id)

    if not user:
        raise LookupError("User not found")

    user.id_verified = True

    db.session.commit()

    return user