from marshmallow import  fields, validate
from schemas.user import UserSchema

class EmployerSchema(UserSchema):
    id = fields.Int(dump_only=True)

    type = fields.String(required=True)
    
    

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
    
    location = fields.String(required=True)
    
class ParentSchema(UserSchema):
    id = fields.Int(dump_only=True)
    name = fields.String(required=True)
    id_card = fields.String()
    picture_upload  = fields.String()

class RecruitmentHistorySchema(Schema):
    id = fields.Int(dump_only=True)
    employer_id = fields.Int(dump_only=True)
    teacher_id = fields.Int(dump_only=True)
    position = fields.Str(required=True)
    hired_at = fields.Date(required=True)
    ended_at = fields.Date(allow_none=True)
    status = fields.Str(dump_only=True)
    
