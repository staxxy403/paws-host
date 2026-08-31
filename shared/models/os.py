from shared.models import BaseSchema


class OSRead(BaseSchema):
    id: int
    family_id: int
    full_name: str
