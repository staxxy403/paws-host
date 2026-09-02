from arq.connections import ArqRedis
from fastapi import APIRouter, Depends, HTTPException
from starlette.types import HTTPExceptionHandler

from api.dependencies import get_arq_pool, valid_user, valid_vps
from api.logic.vps import buy_vps_logic, get_list_vps_logic, get_vps_state_logic
from database.core import VPS, User
from shared.models import VPSActionRequest, VPSPurchaseRequest, VPSRead
from shared.models.responses import success_response

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
        months=body.months,
        arq=arq,
    )
    return success_response(VPSRead.model_validate(vps))


@router.post('/{vps_id}/state')
async def api_change_vps_state(
    body: VPSActionRequest,
    vps: VPS = Depends(valid_vps),
    arq: ArqRedis = Depends(get_arq_pool),
):
    job = await arq.enqueue_job('task_action_vm', vps_id=str(vps.id), action=body.action.value, force=body.force, _job_id=f'action-vps-{vps.id}')
    if not job:
        raise HTTPException(409, 'Worker is busy by another operation with this instance')
    return success_response('queued')


@router.get('/{vps_id}/state')
async def api_get_vps_state(vps: VPS = Depends(valid_vps)):
    vps_state = await get_vps_state_logic(vps=vps)
    return success_response(vps_state)



@router.delete('/{vps_id}')
async def api_delete_vps(
    vps: VPS = Depends(valid_vps),
    arq: ArqRedis = Depends(get_arq_pool),
):
    ...
