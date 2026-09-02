import asyncio

from api.tasks import task_create_vm, task_action_vm
from shared.configs.redis import arq_redis_settings


class WorkerSettings:
    functions = [task_create_vm, task_action_vm]
    redis_settings = arq_redis_settings
