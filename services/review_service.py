from datetime import datetime

from models.video import VideoSubmission
from models.review import Review, ReviewAssignment
from reviewer_service import reviewer_service
from services import rating_service
from extensions import db


def run_ai_review(video_id):
    submission = VideoSubmission.query.get(video_id)

    if not submission:
        raise LookupError("Video submission not found")

    if submission.status != "uploaded":
        raise ValueError("Video submission is not ready for AI review")

    scenario = submission.scenario

    if not scenario:
        raise LookupError("Teaching scenario not found")

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
        raise LookupError("Video submission not found")

    if submission.status != "ai_reviewed":
        raise ValueError("Video submission is not ready for human assignment")

    ai_review = (
        Review.query
        .filter(
            Review.video_id == video_id,
            Review.reviewer_type == "ai",
        )
        .first()
    )

    if not ai_review:
        raise LookupError("AI review not found")

    reviewer = reviewer_service.get_least_loaded_reviewer()

    assignment = ReviewAssignment(
        video_id=video_id,
        reviewer_id=reviewer