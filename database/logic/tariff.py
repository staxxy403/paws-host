from sqlalchemy import select

from database.core import Tariff
from database.core import async_session


async def get_by_id(tariff_id: int, show_only_active: bool = False) -> Tariff | None:
    '''Get Tariff by it's ID. Pass show_only_active=True if this is a purchase of a new instance'''
    async with async_session() as session:
        return await session.scalar(select(Tariff).where(Tariff.id == tariff_id, Tariff.is_active == show_only_active))
