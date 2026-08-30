import uuid
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, joinedload

from shared.enums import VPSStatus

from database.core import VPS, Node, IPAddress
from database.core import async_session


async def get(node_id: int) -> Node | None:
    '''Get Node by ID with its relationships'''
    stmt = (
        select(Node)
        .where(Node.id == node_id)
        .options(
            joinedload(Node.category),
            joinedload(Node.location),
        )
        .options(
            selectinload(Node.ip_pool),
            selectinload(Node.vps_list),
        )
    )

    async with async_session() as session:
        return await session.scalar(stmt)


async def get_used_ram(node_id: int) -> int:
    '''Returns RAM used by Node (count only VPS with status ACTIVE and CREATING)'''
    stmt = (
        select(func.sum(VPS.ram_gb))
        .where(
            VPS.node_id == node_id,
            VPS.status.in_([VPSStatus.ACTIVE, VPSStatus.CREATING])
        )
    )

    async with async_session() as session:
        used_ram = await session.scalar(stmt)

        return used_ram or 0


async def get_available(location_id: int, category_id: int, required_ram_gb: int) -> Node | None:
    '''Returns Node with enough amount of resources to deploy a new VPS'''
    stmt = (
        select(Node)
        .where(
            Node.location_id == location_id,
            Node.category_id == category_id,
            Node.is_active == True,
            Node.ip_pool.any(IPAddress.is_allocated == False)
        )
    )

    async with async_session() as session:
        nodes = await session.scalars(stmt)

        for node in nodes:
            used_ram = await get_used_ram(node.id)
            free_ram = node.max_ram_gb - used_ram

            if free_ram >= required_ram_gb:
                return node

        return None
