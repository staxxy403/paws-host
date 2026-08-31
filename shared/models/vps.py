import uuid

from shared.enums import VPSStatus
from shared.models import BaseSchema, IPAddressRead, LocationRead, OSRead, TariffRead


class VPSRead(BaseSchema):
    id: uuid.UUID
    status: VPSStatus
    expire_at: int

    user_id: uuid.UUID
    ip_id: int
    os_id: int
    tariff_id: int
    location_id: int

    ip_address: IPAddressRead
    os: OSRead
    tariff: TariffRead
    location: LocationRead

class VPSListResponse(BaseSchema):
    vps: list[VPSRead]

class VPSPurchaseRequest(BaseSchema):
    tariff_id: int
    location_id: int
    os_id: int
    months: int
