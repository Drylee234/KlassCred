import random

from models.video import TeachingScenario, VideoSubmission
from models.teacher import Teacher
from api import cencori
from extensions import db


def get_scenario_for_teacher(teacher):
    used_ids = [
        scenario_id
        for (scenario_id,) in (
            db.session.query(VideoSubmission.scenario_id)
            .filter(VideoSubmission.teacher_id == teacher.id)
            .all()
        )
    ]

    query = TeachingScenario.query.filter(
        TeachingScenario.subject.in_(teacher.subjects)
    )

    if used_ids:
        query = query.filter(
            ~TeachingScenario.id.in_(used_ids)
        )

    scenarios = query.all()

    if scenarios:
        return random.choice(scenarios)

    return generate_scenario(teacher)


def generate_scenario(teacher):
    target_level = "secondary"

    # Cencori integration is not implemented yet.
    pass

    # Expected normalized result from the Cencori adapter:
    # {
    #     "prompt_text": ...
    # }

    scenario = TeachingScenario(
        subject=teacher.subjects[0],
        level=target_level,
        prompt_text=result["prompt_text"],
        generated_by="ai",
    )

    db.session.add(scenario)
    db.session.commit()

    return scenario