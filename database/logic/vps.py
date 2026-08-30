from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

from shared.enums import VPSStatus

from database.core import VPS
from database.core import async_session

async def get_vps(vps_id: int) -> VPS | None:
    '''Get VPS by ID with its relationships'''
    stmt = (
        select(VPS)
        .where(VPS.id == vps_id)
        .options(
            joinedload(VPS.ip_address),
            joinedload(VPS.node),
            joinedload(VPS.owner),
            joinedload(VPS.os),
        )
    )
    async with async_session() as session:
        return await session.scalar(stmt)


async def create_vps() -> VPS | None:
    ...


async def delete_vps() -> None:
    ...
