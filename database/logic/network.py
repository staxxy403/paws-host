from sqlalchemy import select
from database.core import async_session
from database.core import IPAddress


async def allocate_ip(node_id: int) -> IPAddress | None:
    '''Set is_allocated=True to the first available IP in the pool'''
    stmt = (
        select(IPAddress)
        .where(
            IPAddress.node_id == node_id,
            IPAddress.is_allocated == False
        )
        .with_for_update(skip_locked=True)
        .limit(1)
    )

    async with async_session() as session:
        ip = await session.scalar(stmt)

        if ip:
            ip.is_allocated = True
            await session.commit()

            await session.refresh(ip)
            return ip

        return None


async def release_ip(ip_id: int) -> None:
    '''Set is_allocated=False to ip by its ID'''
    async with async_session() as session:
        ip = await session.get(IPAddress, ip_id)
        if ip and ip.is_allocated:
            ip.is_allocated = False
            await session.commit()
