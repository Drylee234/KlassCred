from celery_app import celery_app
from extensions import db
from errors.exceptions import RetryableAIServiceError
from models.video import VideoSubmission
from services import review_service


def _mark_submission_failed(video_id):
    db.session.rollback()
    submission = VideoSubmission.query.get(video_id)
    if submission is not None:
        submission.status = "failed"
        db.session.commit()


@celery_app.task(bind=True, max_retries=2)
def review_video_task(self, video_id):
    submission = VideoSubmission.query.get(video_id)
    if submission is None:
        return

    if submission.status != "ai_reviewing":
        return

    try:
        review_service.run_ai_review(video_id)
    except RetryableAIServiceError as e:
        db.session.rollback()
        if self.request.retries < self.max_retries:
            countdown = 30 * (2 ** self.request.retries)
            raise self.retry(exc=e, countdown=countdown)

        _mark_submission_failed(video_id)
        raise
    except Exception:
        _mark_submission_failed(video_id)
        raise
