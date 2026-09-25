from sqlalchemy import String, cast, or_

from models.teacher import Teacher
from models.rating import Rating
from models.employer import Employer
from errors.exceptions import BadRequestError, NotFoundError
from utils.geo import haversine_km
from utils.subjects import validate_subject


def search_teachers(
    subject=None,
    min_rating=None,
    verified_only=True,
    min_experience=None,
    location=None,
    radius_km=None,
    q=None,
    employer_id=None,
):
    if subject is not None:
        validate_subject(subject)

    query = (
        Teacher.query
        .outerjoin(Rating, Rating.teacher_id == Teacher.id)
    )

    if verified_only:
        query = query.filter(Teacher.id_verified.is_(True))

    if min_rating is not None:
        query = query.filter(Rating.composite >= min_rating)

    if min_experience is not None:
        query = query.filter(Teacher.experience_years >= min_experience)

    if location:
        query = query.filter(Teacher.location.ilike(f"%{location.strip()}%"))

    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Teacher.full_name.ilike(like),
                cast(Teacher.subjects, String).ilike(like),
            )
        )

    teachers = query.all()

    # subjects is a JSON list, so membership is checked in Python.
    if subject is not None:
        teachers = [
            teacher
            for teacher in teachers
            if teacher.subjects and subject in teacher.subjects
        ]

    # Distance is measured from the employer's stored coordinates.
    # Teachers without coordinates can't be placed, so they're dropped.
    if radius_km is not None:
        origin_lat, origin_lng = _employer_origin(employer_id)
        nearby = []

        for teacher in teachers:
            if teacher.latitude is None or teacher.longitude is None:
                continue

            distance = haversine_km(
                origin_lat, origin_lng, teacher.latitude, teacher.longitude
            )

            if distance <= radius_km:
                teacher.distance_km = round(distance, 1)
                nearby.append(teacher)

        teachers = sorted(nearby, key=lambda t: t.distance_km)

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


def _employer_origin(employer_id):
    employer = Employer.query.get(employer_id) if employer_id else None

    if not employer:
        raise NotFoundError("Employer profile not found.")

    if employer.latitude is None or employer.longitude is None:
        raise BadRequestError(
            "Add your location (latitude/longitude) to your profile "
            "to filter by distance."
        )

    return employer.latitude, employer.longitude