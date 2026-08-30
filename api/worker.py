import asyncio
from shared.configs.redis import arq_redis_settings

async def task_create_vm(ctx, vps_id: int):
    ...

class WorkerSettings:
    functions = [task_create_vm]
    redis_settings = arq_redis_settings
