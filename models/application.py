from marshmallow import Schema, fields, validate
from schemas.teacher import TeacherPublicSchema


class ApplicationCreateSchema(Schema):
    employer_id = fields.Int(required=True, validate=validate.Range(min=1))
    position = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    message = fields.Str(allow_none=True, validate=validate.Length(max=2000))


class ApplicationRespondSchema(Schema):
    status = fields.Str(required=True, validate=validate.OneOf(["accepted", "rejected"]))


class ApplicationSchema(Schema):
    id = fields.Int(dump_only=True)
    employer_id = fields.Int(dump_only=True)
    teacher_id = fields.Int(dump_only=True)
    employer_name = fields.Method("get_employer_name")
    teacher = fields.Nested(TeacherPublicSchema, dump_only=True)
    position = fields.Str(dump_only=True)
    message = fields.Str(dump_only=True)
    status = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    def get_employer_name(self, obj):
        e = obj.employer
        return getattr(e, "org_name", None) or getattr(e, "name", None)
