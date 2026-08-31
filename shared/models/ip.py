from shared.models import BaseSchema


class IPAddressRead(BaseSchema):
    id: int
    ip: str
    is_allocated: bool
