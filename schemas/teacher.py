from marshmallow import Schema, fields, validate
from schemas.user import UserSchema


class WorkHistorySchema(Schema):
    id = fields.Int(dump_only=True)
    organization = fields.Str(required=True)
    role = fields.Str(required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(allow_none=True)


class ReferenceSchema(Schema):
    id = fields.Int(dump_only=True)
    full_name = fields.Str(required=True)
    organization = fields.Str(allow_none=True)   
    role = fields.Str(allow_none=True)           
    email = fields.Email(required=True)
    phone = fields.Str(required=True)
    relationship_type = fields.Str(required=True)


class TeacherSchema(UserSchema):
    id = fields.Int(dump_only=True)

    full_name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=100)
    )

    subjects = fields.List(
        fields.Str(),
        required=True
    )

    experience_years = fields.Int(
        required=True,
        validate=validate.Range(min=0)
    )

    id_verified = fields.Bool(dump_only=True)
    profile_complete = fields.Bool(dump_only=True)
    documents = fields.Dict(
        allow_none=True,
        load_default=None
    )

    work_history = fields.List(
        fields.Nested(WorkHistorySchema),
        required=False
    )

    references = fields.List(
        fields.Nested(ReferenceSchema),
        required=False
    )

    created_at = fields.DateTime(dump_only=True)
