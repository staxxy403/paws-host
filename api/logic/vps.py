import time
import uuid

from arq import ArqRedis
from database.logic import vps as vps_logic
from database.logic import finance as finance_logic
from database.logic import network as network_logic
from database.logic import tariff as tariff_logic
from database.logic import location as location_logic
from database.logic import node as node_logic
from database.logic import os as os_logic

from database.core import VPS

from fastapi import HTTPException
from shared.models import VPSListResponse
from shared.models.responses import success_response

SECONDS_IN_MONTH = 30 * 24 * 60 * 60


async def get_list_vps_logic(user_id: uuid.UUID) -> VPSListResponse:
    vps_list = await vps_logic.get_list_by_user_id(user_id=user_id)

    return success_response(
        VPSListResponse(
            vps=vps_list
        )
    )


async def buy_vps_logic(user_id: uuid.UUID, tariff_id: int, location_id: int, os_id: int, months: int, arq: ArqRedis) -> VPS:
    tariff = await tariff_logic.get_by_id(tariff_id=tariff_id, show_only_active=True)
    if not tariff:
        raise HTTPException(400, f'Tariff {tariff_id} not found or not available for purchase')

    if months < 1 or months > 12:
        raise HTTPException(400, 'Invalid billing period')

    expire_at = int(time.time()) + (months * SECONDS_IN_MONTH)
    total_price = months * tariff.price

    location = await location_logic.get_by_id(location_id=location_id)
    if not location:
        raise HTTPException(400, f'Location {location_id} not found')

    node = await node_logic.get_available(location_id=location_id, category_id=tariff.category_id, required_ram_gb=tariff.ram_gb)
    if not node:
        raise HTTPException(400, 'No available resources in the selected region. Please try another location')

    os = await os_logic.get_by_id(os_id=os_id)
    if not os:
        raise HTTPException(400, f'OS {os_id} not found')

    try:
        await finance_logic.charge_user(user_id=user_id, amount=total_price)
    except ValueError as e:
        raise HTTPException(400, str(e))

    ip = await network_logic.allocate_ip(node.id)
    if not ip:
        await finance_logic.credit_user(user_id=user_id, amount=total_price)
        raise HTTPException(503, 'Out of IP-addresses. Money refunded')

    vps = await vps_logic.create(
        user_id = user_id,
        node_id = node.id,
        ip_id = ip.id,
        os_id = os.id,
        tariff_id=tariff_id,
        expire_at=expire_at,
    )

    await arq.enqueue_job('task_create_vm', vps_id=str(vps.id), paid_amount=total_price, _job_id=f'create-vps-{vps.id}')
    return vps
