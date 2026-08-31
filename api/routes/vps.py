from arq.connections import ArqRedis
from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_arq_pool, valid_user, valid_vps
from api.logic.vps import buy_vps_logic, get_list_vps_logic
from database.core import VPS, User
from shared.models import VPSRead, VPSPurchaseRequest
from shared.models.responses import success_response
from starlette.types import HTTPExceptionHandler

router = APIRouter(prefix='/vps')


@router.get('')
async def api_get_vps_list(current_user: User = Depends(valid_user)):
    return await get_list_vps_logic(user_id=current_user.id)


@router.get('/{vps_id}')
async def api_get_vps(vps: VPS = Depends(valid_vps)):
    return success_response(VPSRead.model_validate(vps))


@router.post('/buy')
async def api_buy_vps(
    body: VPSPurchaseRequest,
    current_user: User = Depends(valid_user),
    arq: ArqRedis = Depends(get_arq_pool),
):
    vps = await buy_vps_logic(
        user_id=current_user.id,
        tariff_id=body.tariff_id,
        location_id=body.location_id,
        os_id=body.os_id,
        months=body.months
    )

    await arq.enqueue_job('task_create_vm', str(vps.id))
    return success_response(VPSRead.model_validate(vps))


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
