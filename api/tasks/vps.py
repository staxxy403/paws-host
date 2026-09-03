import logging
import uuid
from coolname import generate_slug
import secrets

from arq import Retry

from jinja2 import Environment, FileSystemLoader

from api.tasks.json_builders import vm_create_payload, vm_action_payload
from api.utils import IncusClient
from database.logic import finance, network
from database.logic import vps as vps_logic
from shared.enums import VPSStatus, VPSAction
from shared.exceptions import IncusNodeUnreachableError, IncusOperationError

logger = logging.getLogger(__name__)
jinja_env = Environment(loader=FileSystemLoader('shared/templates'))


async def task_create_vm(ctx, vps_id: uuid.UUID, paid_amount: int):
    vps = await vps_logic.get_by_id(vps_id)

    if not vps or vps.status != VPSStatus.CREATING:
        logger.warning(f'VPS {vps_id} not found or not in "CREATING" status')
        return

    root_password = secrets.token_urlsafe(12)
    hostname = generate_slug(2)

    user_data_template = jinja_env.get_template('cloud_init.yml.j2')
    user_data_yaml = user_data_template.render(
        hostname=hostname,
        root_password=root_password,
        ssh_keys=[]
    )

    network_template = jinja_env.get_template('network_config.yml.j2')
    network_yaml = network_template.render(
        ip_address=vps.ip_address.ip
    )

    try:
        async with IncusClient(node=vps.node) as incus:
            await incus.request(
                'POST', '/instances', wait=True,
                json = vm_create_payload(vps=vps, user_data_yaml=user_data_yaml, network_data_yaml=network_yaml)
            )
            await vps_logic.update_status(vps.id, VPSStatus.ACTIVE)

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


async def task_action_vm(ctx, vps_id: uuid.UUID, action: str, force: bool):
    vps = await vps_logic.get_by_id(vps_id)

    if not vps or vps.status != VPSStatus.ACTIVE:
        logger.warning(f'VPS {vps_id} not found or not in "ACTIVE" status')
        return

    try:
        async with IncusClient(node=vps.node) as incus:
            await incus.request('PUT', f'/instances/{vps.incus_name}/state', wait=True, json=vm_action_payload(action=action, force=force))

    except IncusOperationError as e:
        logger.error(f'Error while {action} instance: {e}')
        return

    except IncusNodeUnreachableError:
        if ctx['job_try'] < 3:
            raise Retry(defer=20)
        logger.error(f'Node {vps.node_id} unreachable after 3 retries')
        return


async def task_delete_vm(ctx, vps_id: uuid.UUID):
    vps = await vps_logic.get_by_id(vps_id)

    if not vps or vps.status not in (VPSStatus.ACTIVE, VPSStatus.ERROR):
        logger.warning(f'VPS {vps_id} not found or not in "ACTIVE, ERROR" status')
        return

    try:
        async with IncusClient(node=vps.node) as incus:
            try:
                await incus.request('PUT', f'/instances/{vps.incus_name}/state', wait=True, json=vm_action_payload(action='stop', force=True))
            except Exception as e:
                logger.error(f'Error while stop instance: {e}')

            await incus.request('DELETE', f'/instances/{vps.incus_name}', wait=True)
            await network.release_ip(ip_id=vps.ip_address.id)
            await vps_logic.update_status(vps_id=vps.id, new_status=VPSStatus.DELETED)

    except IncusOperationError as e:
        logger.error(f'Error while delete instance: {e}')
        return

    except IncusNodeUnreachableError:
        if ctx['job_try'] < 3:
            raise Retry(defer=20)
        logger.error(f'Node {vps.node_id} unreachable after 3 retries')
        return
