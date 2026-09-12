from datetime import datetime

from models.video import VideoSubmission
from models.review import Review, ReviewAssignment
from services import reviewer_service, rating_service
from extensions import db
from errors.exceptions import NotFoundError, BadRequestError, ForbiddenError


def run_ai_review(video_id):
    submission = VideoSubmission.query.get(video_id)

    if not submission:
        raise NotFoundError("Video submission not found")

    if submission.status != "uploaded":
        raise BadRequestError("Video submission is not ready for AI review")

    scenario = submission.scenario

    if not scenario:
        raise NotFoundError("Teaching scenario not found")

    # Cencori integration is not implemented yet.
    pass

    # Expected normalized result from the Cencori adapter:
    # {
    #     "score": ...,
    #     "notes": ...,
    #     "flagged": ...,
    #     "flag_reason": ...
    # }

    review = Review(
        video_id=video_id,
        reviewer_id=None,
        reviewer_type="ai",
        score=result["score"],
        notes=result["notes"],
        flagged=result["flagged"],
        flag_reason=result.get("flag_reason"),
    )

    submission.status = "ai_reviewed"

    db.session.add(review)
    db.session.commit()

    assignment = assign_human_reviewer(video_id)

    return {
        "review": review,
        "assignment": assignment,
    }


def assign_human_reviewer(video_id):
    submission = VideoSubmission.query.get(video_id)

    if not submission:
        raise NotFoundError("Video submission not found")

    if submission.status != "ai_reviewed":
        raise BadRequestError("Video submission is not ready for human assignment")

    ai_review = (
        Review.query
        .filter(
            Review.video_id == video_id,
            Review.reviewer_type == "ai",
        )
        .first()
    )

    if not ai_review:
        raise NotFoundError("AI review not found")

    reviewer = reviewer_service.get_least_loaded_reviewer()

    assignment = ReviewAssignment(
        video_id=video_id,
        reviewer_id=reviewer.id,
        status="assigned",
    )

    submission.status = "assigned"

    db.session.add(assignment)
    db.session.commit()

    return assignment


def get_assignments_for_reviewer(reviewer_id):
    return (
        ReviewAssignment.query
        .filter_by(reviewer_id=reviewer_id)
        .order_by(ReviewAssignment.assigned_at.desc())
        .all()
    )


def submit_human_review(reviewer_id, assignment_id, data):
    assignment = ReviewAssignment.query.get(assignment_id)

    if not assignment:
        raise NotFoundError("Assignment not found")

    if assignment.reviewer_id != reviewer_id:
        raise ForbiddenError("You do not own this assignment")

    if assignment.status == "completed":
        raise BadRequestError("This assignment is already completed")

    if assignment.status == "cancelled":
        raise BadRequestError("This assignment has been cancelled")

    review = Review(
        video_id=assignment.video_id,
        reviewer_id=reviewer_id,
        reviewer_type="human",
        score=data["score"],
        notes=data.get("notes"),
        flagged=data["flagged"],
        flag_reason=data.get("flag_reason"),
    )

    assignment.status = "completed"
    assignment.completed_at = datetime.utcnow()

    submission = VideoSubmission.query.get(assignment.video_id)

    if submission:
        submission.status = "completed"

    db.session.add(review)
    db.session.commit()

    rating_service.recompute_rating(submission.teacher_id)

    return review