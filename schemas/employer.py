from marshmallow import Schema, fields, validate
from schemas.user import UserSchema


class EmployerSchema(UserSchema):
    id = fields.Int(dump_only=True)

    # Reference point for distance search (set by the client).
    latitude = fields.Float(allow_none=True, validate=validate.Range(min=-90, max=90))
    longitude = fields.Float(allow_none=True, validate=validate.Range(min=-180, max=180))


class OrganizationSchema(EmployerSchema):
    id = fields.Int(dump_only=True)

    org_name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=150)
    )

    cac_number = fields.Str(
        allow_none=True,
        validate=validate.Length(max=50)
    )

    location = fields.Str(required=True)


class ParentSchema(EmployerSchema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    id_card = fields.Str(allow_none=True)
    picture_upload = fields.Str(allow_none=True)


class RecruitmentHistorySchema(Schema):
    id = fields.Int(dump_only=True)
    employer_id = fields.Int(dump_only=True)
    teacher_id = fields.Int(dump_only=True)
    position = fields.Str(required=True)
    hired_at = fields.Date(required=True)
    ended_at = fields.Date(allow_none=True)
    status = fields.Str(dump_only=True)