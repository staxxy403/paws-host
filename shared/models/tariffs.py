from shared.models import BaseSchema


class TariffRead(BaseSchema):
    id: int
    category_id: int

    disk_gb: int
    ram_gb: int
    cpu_cores: int

    price: int
    is_active: bool
