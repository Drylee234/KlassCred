from marshmallow import Schema, fields, validate


class ReviewAssignmentSchema(Schema):
    id = fields.Int(dump_only=True)

    video_id = fields.Int(required=True)
    reviewer_id = fields.Int(required=True)

    # FIX: aligned with model enum ("assigned","in_progress","completed","cancelled")
    status = fields.Str(
        dump_only=True,
        validate=validate.OneOf([
            "assigned",
            "in_progress",
            "completed",
            "cancelled"
        ])
    )

    assigned_at = fields.DateTime(dump_only=True)
    completed_at = fields.DateTime(dump_only=True)


class ReviewSchema(Schema):
    id = fields.Int(dump_only=True)

    video_id = fields.Int(required=True)

    reviewer_id = fields.Int(
        allow_none=True,
        dump_only=True
    )

    reviewer_type = fields.Str(
        required=True,
        validate=validate.OneOf(["ai", "human"])
    )

    score = fields.Float(
        allow_none=True,
        validate=validate.Range(min=0, max=100)
    )

    notes = fields.Str(allow_none=True)

    flagged = fields.Bool(dump_only=True)
    flag_reason = fields.Str(dump_only=True)

    created_at = fields.DateTime(dump_only=True)


class HumanReviewSubmitSchema(Schema):
    score = fields.Float(
        required=True,
        validate=validate.Range(min=0, max=100)
    )

    notes = fields.Str(allow_none=True)

    flagged = fields.Bool(required=True)

    flag_reason = fields.Str(allow_none=True)
