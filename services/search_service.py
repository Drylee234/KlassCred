from models.teacher import Teacher
from models.rating import Rating
from models.user import User


def search_teachers(
    subject=None,
    min_rating=None,
    verified_only=True,
):
    query = (
        Teacher.query
        .outerjoin(Rating, Rating.teacher_id == Teacher.id)
    )

    if verified_only:
        query = query.filter(User.id_verified.is_(True))

    teachers = query.all()

    if subject is not None:
        teachers = [
            teacher
            for teacher in teachers
            if teacher.subjects and subject in teacher.subjects
        ]

    if min_rating is not None:
        teachers = [
            teacher
            for teacher in teachers
            if teacher.rating
            and teacher.rating.composite is not None
            and teacher.rating.composite >= min_rating
        ]

    # Exclude any teacher with a flagged review on any video submission.
    # A human reviewer flag means a safety/pedagogy concern was raised —
    # that teacher should not be discoverable by employers regardless of
    # their numeric score, until the flag is manually resolved.
    teachers = [
        teacher
        for teacher in teachers
        if not any(
            review.flagged
            for submission in teacher.video_submissions
            for review in submission.reviews
        )
    ]

    return teachers
