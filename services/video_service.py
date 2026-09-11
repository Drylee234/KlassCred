from datetime import datetime

from models.video import VideoSubmission, TeachingScenario
from services import review_service
from extensions import db
from errors.exceptions import NotFoundError
from api import cloudinary as cloudinary_api


def request_upload_url(teacher_id, scenario_id):
    # Ownership is enforced by the route/auth layer.
    scenario = TeachingScenario.query.get(scenario_id)

    if not scenario:
        raise NotFoundError("Teaching scenario not found")

    # Cloudinary integration is not implemented yet.
    pass

    # Expected normalized result from the Cloudinary adapter:
    # {
    #     "upload_url": ...,
    #     "scenario_id": scenario_id
    # }

    return result


def confirm_upload(teacher_id, scenario_id, video_url):
    # Ownership is enforced by the route/auth layer.
    scenario = TeachingScenario.query.get(scenario_id)

    if not scenario:
        raise NotFoundError("Teaching scenario not found")

    existing = (
        VideoSubmission.query
        .filter_by(video_url=video_url)
        .first()
    )

    if existing:
        return existing

    submission = VideoSubmission(
        teacher_id=teacher_id,
        scenario_id=scenario_id,
        video_url=video_url,
        status="uploaded",
        uploaded_at=datetime.utcnow(),
    )

    db.session.add(submission)
    db.session.commit()

    review_service.run_ai_review(submission.id)

    return submission


def handle_cloudinary_webhook(payload):
    # Cloudinary webhook signature verification is not implemented yet.
    pass

    video_url = payload["video_url"]
    teacher_id = payload["teacher_id"]
    scenario_id = payload["scenario_id"]

    existing = (
        VideoSubmission.query
        .filter_by(video_url=video_url)
        .first()
    )

    if existing:
        if existing.status == "uploaded":
            review_service.run_ai_review(existing.id)

        return existing

    return confirm_upload(
        teacher_id,
        scenario_id,
        video_url,
    )