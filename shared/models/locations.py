from shared.models import BaseSchema


class LocationRead(BaseSchema):
    id: int
    display_name: str
    country_code: str
