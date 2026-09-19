from sqlalchemy import func

from models.reviewer import Reviewer
from models.review import ReviewAssignment
from extensions import db
from errors.exceptions import NotFoundError


# Assignments in these states count as "active load" on a reviewer.
# Completed/cancelled assignments free up their capacity.
_ACTIVE_STATUSES = ("assigned", "in_progress")


def get_least_loaded_reviewer():
    """
    Returns the vetted human reviewer with the fewest currently active
    (assigned or in_progress) review assignments -- a simple round-robin
    load balancer so no single reviewer gets buried while others sit idle.

    Raises NotFoundError if there are no reviewers registered at all.
    """
    reviewer = (
        db.session.query(Reviewer)
        .outerjoin(
            ReviewAssignment,
            db.and_(
                ReviewAssignment.reviewer_id == Reviewer.id,
                ReviewAssignment.status.in_(_ACTIVE_STATUSES),
            ),
        )
        .group_by(Reviewer.id)
        .order_by(func.count(ReviewAssignment.id).asc())
        .first()
    )

    if not reviewer:
        raise NotFoundError("No reviewers are available to assign this video to.")

    return reviewer
