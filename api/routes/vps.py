from fastapi import APIRouter, Depends
from arq.connections import ArqRedis

from api.dependencies import valid_user, valid_vps, get_arq_pool
from database.core import VPS, User

from api.logic.vps import get_list_vps_logic
from shared.models.responses import success_response
from shared.models import VPSRead

router = APIRouter(prefix='/vps')


@router.get('')
async def api_get_vps_list(current_user: User = Depends(valid_user)):
    return await get_list_vps_logic(user_id=current_user.id)


@router.get('/{vps_id}')
async def api_get_vps(vps: VPS = Depends(valid_vps)):
    return success_response(VPSRead.model_validate(vps))


@router.post('/buy')
async def api_buy_vps(
    current_user: User = Depends(valid_user),
    arq: ArqRedis = Depends(get_arq_pool),
):
    ...


@router.post('/{vps_id}/action')
async def api_action_with_vps(
    vps: VPS = Depends(valid_vps),
    arq: ArqRedis = Depends(get_arq_pool),
):
    ...


@router.delete('/{vps_id}')
async def api_delete_vps(
    vps: VPS = Depends(valid_vps),
    arq: ArqRedis = Depends(get_arq_pool),
):
    ...
