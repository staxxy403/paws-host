import os
import uuid

from fastapi import Depends, Header, HTTPException

from database.core import VPS, User
from database.logic import user as user_logic
from database.logic import vps as vps_logic
from shared.enums import VPSStatus

API_SECRET_KEY = os.getenv('API_SECRET_KEY')
if not API_SECRET_KEY:
    raise RuntimeError('API_SECRET_KEY is not configured in .env')


async def valid_user(x_telegram_token: str = Header(...), x_user_id: int = Header(...)) -> User:
    '''Authenticate user from Telegram bot'''
    if x_telegram_token != API_SECRET_KEY:
        raise HTTPException(status_code=403, detail='Wrong API Key')

    user = await user_logic.get_by_tg_id(telegram_id=x_user_id)

    if not user:
        user = await user_logic.create(telegram_id=x_user_id)

    return user


async def valid_vps(vps_id: uuid.UUID, user: User = Depends(valid_user)) -> VPS:
    '''Get VPS of authenticated user'''
    vps = await vps_logic.get_by_id(vps_id)

    if not vps or vps.user_id != user.id or vps.status in (VPSStatus.DELETED,):
        raise HTTPException(status_code=404, detail="VPS not found")

    return vps
