from sqlalchemy import select

from database.core import Location
from database.core import async_session


async def get_by_id(location_id: int) -> Location | None:
    '''Get Location by it's ID.'''
    async with async_session() as session:
        return await session.get(Location, location_id)
