from errors.exceptions import BadRequestError

# Single source of truth for allowed subjects.
# Keep in sync with SUBJECTS in static/common.js.
SUBJECTS = [
    "Mathematics", "Further Mathematics", "English", "Literature",
    "Physics", "Chemistry", "Biology", "Computer Science", "Economics",
    "Government", "Geography", "History", "Civic Education", "Commerce",
    "Accounting", "Agricultural Science",
]


def validate_subject(subject):
    if subject not in SUBJECTS:
        raise BadRequestError(f"Invalid subject: {subject!r}.")
    return subject


def validate_subjects(subjects):
    """Return a de-duplicated list, or raise if empty / not in SUBJECTS."""
    if not isinstance(subjects, list) or not subjects:
        raise BadRequestError("At least one subject is required.")
    invalid = [s for s in subjects if s not in SUBJECTS]
    if invalid:
        raise BadRequestError(f"Invalid subject(s): {', '.join(map(str, invalid))}.")
    return list(dict.fromkeys(subjects))
