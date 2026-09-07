from marshmallow import Schema, fields, validate


class RatingSchema(Schema):
    id = fields.Int(dump_only=True)

    teacher_id = fields.Int(required=True)

    exam_score = fields.Float(allow_none=True)
    video_score = fields.Float(allow_none=True)
    reference_score = fields.Float(allow_none=True)
    profile_score = fields.Float(allow_none=True)

    composite = fields.Float(dump_only=True)

    overridden = fields.Bool(dump_only=True)
    override_reason = fields.Str(dump_only=True)

    breakdown = fields.Dict(dump_only=True)

    updated_at = fields.DateTime(dump_only=True)
