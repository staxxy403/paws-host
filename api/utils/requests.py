import os
import httpx
from database.core import Node

from shared.exceptions import (
    IncusError,
    IncusNodeUnreachableError,
    IncusOperationError,
)

INCUS_CLIENT_CERT_PATH = os.getenv('INCUS_CLIENT_CERT_PATH')
INCUS_CLIENT_KEY_PATH = os.getenv('INCUS_CLIENT_KEY_PATH')

if not (INCUS_CLIENT_CERT_PATH and INCUS_CLIENT_KEY_PATH):
    raise RuntimeError('Incus certificates are not configured in .env')


class IncusClient:
    def __init__(self, node: Node, project: str = 'default'):
        self.base_url = f'https://{node.ip_address}:{node.api_port}/1.0'
        self.project = project

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            cert=(INCUS_CLIENT_CERT_PATH, INCUS_CLIENT_KEY_PATH),
            verify=False,
            timeout=60.0
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def request(self, method: str, path: str, **kwargs) -> dict:
        '''Base Incus request. Checks response["type"] and HTTP status-codes by Incus specification'''
        params = kwargs.pop('params', {})
        if self.project != 'default' and 'project' not in params:
            params['project'] = self.project

        try:
            res = await self.client.request(method, path, params=params, **kwargs)
        except (httpx.ConnectError, httpx.ConnectTimeout) as e:
            raise IncusNodeUnreachableError(f'Node {self.base_url} is unreachable') from e

        if res.is_error:
            try:
                error_body = res.json()
                err_msg = error_body.get('error') or res.text
                err_code = error_body.get('error_code') or res.status_code
            except Exception:
                err_msg = res.text
                err_code = res.status_code
            raise IncusError(f'Incus API Error [{err_code}]: {err_msg}')

        data = res.json()
        return data

    async def wait_operation(self, operation_path_or_url: str, timeout: float = 300.0) -> dict:
        '''Wait Incus async operation'''
        op_id = operation_path_or_url.split('/')[-1]

        res_data = await self.request(
            'GET',
            f'/operations/{op_id}/wait',
            params={'timeout': int(timeout)},
            timeout=timeout
        )

        metadata = res_data.get('metadata', {})

        op_status_code = metadata.get('status_code')

        if op_status_code == 200:
            return metadata

        error_msg = metadata.get('err') or metadata.get('status') or 'Unknown operation error'
        raise IncusOperationError(
            message=f'Incus Operation [{op_id}] failed with status code {op_status_code}: {error_msg}',
            operation_id=op_id,
            raw_data=metadata
        )
