from models.reviewer import Reviewer
from models.review import ReviewAssignment
from errors.exceptions import NotFoundError


def get_workload(reviewer_id):
    return (
        ReviewAssignment.query
        .filter(
            ReviewAssignment.reviewer_id == reviewer_id,
            ReviewAssignment.status.in_(["assigned", "in_progress"])
        )
        .count()
    )


def get_least_loaded_reviewer():
    reviewers = Reviewer.query.all()

    if not reviewers:
        raise NotFoundError("No reviewers available")

    reviewer_workloads = []

    for reviewer in reviewers:
        workload = get_workload(reviewer.id)

        most_recent_assignment = (
            ReviewAssignment.query
            .filter_by(reviewer_id=reviewer.id)
            .order_by(ReviewAssignment.assigned_at.desc())
            .first()
        )

        reviewer_workloads.append(
            (
                reviewer,
                workload,
                most_recent_assignment.assigned_at
                if most_recent_assignment
                else None,
            )
        )

    reviewer_workloads.sort(
        key=lambda item: (
            item[1],
            item[2] is not None,
            item[2] if item[2] is not None else 0,
        )
    )

    return reviewer_workloads[0][0]