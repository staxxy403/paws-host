from sqlalchemy import select

from database.core import OS
from database.core import async_session


async def get_by_id(os_id: int) -> OS | None:
    '''Get OS by it's ID.'''
    async with async_session() as session:
        return await session.get(OS, os_id)
