from models.rating import Rating
from models.exam import ExamAttempt
from models.review import Review
from models.video import VideoSubmission
from models.teacher import Teacher
from extensions import db

from errors.exceptions import NotFoundError, ForbiddenError, BadRequestError


EXAM_WEIGHT = 40
VIDEO_WEIGHT = 35
REFERENCE_WEIGHT = 15
PROFILE_WEIGHT = 10


def recompute_rating(teacher_id):
    """
    Recompute and persist a teacher's composite rating.

    All component scores use a 0–100 scale.
    Missing components are excluded and their weights are
    redistributed proportionally among the available components.
    """

    teacher = Teacher.query.get(teacher_id)

    if not teacher:
        raise NotFoundError("Teacher not found")

    # ---------------------------------------------------------
    # Exam score
    # ---------------------------------------------------------

    latest_exam = (
        ExamAttempt.query
        .filter_by(
            teacher_id=teacher_id,
            completed=True
        )
        .order_by(ExamAttempt.submitted_at.desc())
        .first()
    )

    exam_score = latest_exam.score if latest_exam else None

    # ---------------------------------------------------------
    # Video score
    # ---------------------------------------------------------

    latest_human_review = (
        Review.query
        .join(VideoSubmission, Review.video_id == VideoSubmission.id)
        .filter(
            VideoSubmission.teacher_id == teacher_id,
            Review.reviewer_type == "human"
        )
        .order_by(Review.created_at.desc())
        .first()
    )

    video_score = latest_human_review.score if latest_human_review else None

    # ---------------------------------------------------------
    # Reference score
    # ---------------------------------------------------------

    reference_score = (
        100.0
        if teacher.references
        else None
    )

    # ---------------------------------------------------------
    # Profile score
    # ---------------------------------------------------------

    profile_score = (
        100.0
        if teacher.profile_complete
        else 0.0
    )

    # ---------------------------------------------------------
    # Build available components
    # ---------------------------------------------------------

    components = {
        "exam": {
            "score": exam_score,
            "weight": EXAM_WEIGHT
        },
        "video": {
            "score": video_score,
            "weight": VIDEO_WEIGHT
        },
        "reference": {
            "score": reference_score,
            "weight": REFERENCE_WEIGHT
        },
        "profile": {
            "score": profile_score,
            "weight": PROFILE_WEIGHT
        }
    }

    available = {
        name: data
        for name, data in components.items()
        if data["score"] is not None
    }

    if not available:
        composite = None
        breakdown = {}
    else:
        total_available_weight = sum(
            data["weight"]
            for data in available.values()
        )

        composite = 0.0
        breakdown = {}

        for name, data in available.items():
            effective_weight = (
                data["weight"] / total_available_weight
            )

            composite += (
                data["score"] * effective_weight
            )

            breakdown[name] = {
                "score": data["score"],
                "weight": data["weight"],
                "effective_weight": effective_weight
            }

        composite = round(composite, 2)

    # ---------------------------------------------------------
    # Create or update rating
    # ---------------------------------------------------------

    rating = Rating.query.filter_by(
        teacher_id=teacher_id
    ).first()

    if not rating:
        rating = Rating(teacher_id=teacher_id)
        db.session.add(rating)

    rating.exam_score = exam_score
    rating.video_score = video_score
    rating.reference_score = reference_score
    rating.profile_score = profile_score
    rating.composite = composite
    rating.breakdown = breakdown

    db.session.commit()

    return rating


def override_rating(
    teacher_id,
    composite,
    reason
):
    """
    Manually override a teacher's composite rating.

    Authorization for who may perform the override belongs
    to the route/service caller responsible for reviewer
    permissions.
    """

    if composite is None or not 0 <= composite <= 100:
        raise BadRequestError(
            "Composite rating must be between 0 and 100"
        )

    if not reason or not reason.strip():
        raise BadRequestError(
            "Override reason is required"
        )

    teacher = Teacher.query.get(teacher_id)

    if not teacher:
        raise NotFoundError("Teacher not found")

    rating = Rating.query.filter_by(
        teacher_id=teacher_id
    ).first()

    if not rating:
        rating = Rating(teacher_id=teacher_id)
        db.session.add(rating)

    rating.composite = float(composite)
    rating.overridden = True
    rating.override_reason = reason.strip()

    db.session.commit()

    return rating