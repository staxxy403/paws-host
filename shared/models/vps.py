import uuid

from database.core import VPS
from shared.enums import VPSStatus, VPSAction
from sqlalchemy.sql.expression import false

from .base import BaseSchema
from .ip import IPAddressRead
from .locations import LocationRead
from .os import OSRead
from .tariffs import TariffRead


class VPSRead(BaseSchema):
    id: uuid.UUID
    status: VPSStatus
    expire_at: int

    user_id: uuid.UUID
    ip_id: int
    os_id: int
    tariff_id: int

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

class VPSActionRequest(BaseSchema):
    action: VPSAction
    force: bool | None = False

class VPSLiveState(BaseSchema):
    status: str
    ram_usage: int
    ram_total: int
    ram_percent: float
    ip: str

class VPSStateRead(VPSRead):
    state: VPSLiveState
