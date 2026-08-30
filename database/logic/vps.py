import uuid
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from shared.enums import VPSStatus

from database.core import VPS, Node, OS
from database.core import async_session


async def get(vps_id: int) -> VPS | None:
    '''Get VPS by ID with its relationships'''
    stmt = (
        select(VPS)
        .where(VPS.id == vps_id)
        .options(
            joinedload(VPS.ip_address),
            joinedload(VPS.node),
            joinedload(VPS.owner),

            joinedload(VPS.os).joinedload(OS.family),
            joinedload(VPS.node).joinedload(Node.location),
            joinedload(VPS.node).joinedload(Node.category),
        )
    )
    async with async_session() as session:
        return await session.scalar(stmt)


async def create(
    user_id: int,
    node_id: int,
    ip_id: int,
    os_id: int,
    tariff_id: int,
    cpu_cores: int,
    ram_gb: int,
    disk_gb: int,
    expire_at: int
) -> VPS:
    '''Create new VPS with status = VPSStatus.CREATING'''

    new_vps = VPS(
        uuid=str(uuid.uuid4()),
        user_id=user_id,
        node_id=node_id,
        ip_id=ip_id,
        os_id=os_id,
        tariff_id=tariff_id,
        cpu_cores=cpu_cores,
        ram_gb=ram_gb,
        disk_gb=disk_gb,
        expire_at=expire_at,
        status=VPSStatus.CREATING,
    )

    async with async_session() as session:
        session.add(new_vps)
        await session.commit()
        await session.refresh(new_vps)
        return new_vps


async def update_status(vps_id: int, new_status: VPSStatus) -> None:
    '''Update VPS status'''
    async with async_session() as session:
        vps = await session.get(VPS, vps_id)
        if vps:
            vps.status = new_status
            await session.commit()
