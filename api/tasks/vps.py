import logging
import uuid

from arq import Retry

from api.tasks.json_builders import vm_create_payload
from api.utils import IncusClient
from database.logic import finance
from database.logic import vps as vps_logic
from shared.enums import VPSStatus
from shared.exceptions import IncusNodeUnreachableError, IncusOperationError

logger = logging.getLogger(__name__)


async def task_create_vm(ctx, vps_id: uuid.UUID, paid_amount: int):
    vps = await vps_logic.get(vps_id)

    if not vps or vps.status != VPSStatus.CREATING:
        logger.warning(f'VPS {vps_id} not found or not in "CREATING" status')
        return

    try:
        res = await IncusClient.request(
            'POST', '/instances',
            json = vm_create_payload(vps=vps)
        )
        operation = res.get('operation')

        if operation:
            logger.debug(f'operation_id: {operation}')
            await IncusClient.wait_operation(operation)

    except IncusOperationError as e:
        logger.error(f'Error while creating instance: {e}')
        await vps_logic.update_status(vps_id, VPSStatus.ERROR)
        await finance.credit_user(user_id=vps.user_id, amount=paid_amount)
        return

    except IncusNodeUnreachableError:
        if ctx['job_try'] < 3:
            raise Retry(defer=20)
        logger.error(f'Node {vps.node_id} unreachable after 3 retries')
        await vps_logic.update_status(vps_id, VPSStatus.ERROR)
        await finance.credit_user(user_id=vps.user_id, amount=paid_amount)
        return
