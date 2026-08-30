from sqlalchemy import select

from database.core import User
from database.core import async_session


async def get_user(user_id: int) -> User | None:
    '''Get User by ID'''
    async with async_session() as session:
        return await session.get(User, user_id)


async def get_user_by_tg_id(telegram_id: int) -> User | None:
    '''Get User by Telegram ID'''
    stmt = select(User).where(User.telegram_id == telegram_id)
    async with async_session() as session:
        return await session.scalar(stmt)


async def create_user(telegram_id: int) -> User:
    '''Create new User'''
    new_user = User(telegram_id=telegram_id)
    async with async_session() as session:
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
