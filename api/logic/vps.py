import uuid

from database.logic import vps as vps_logic
from shared.models import VPSListResponse
from shared.models.responses import success_response


async def get_list_vps_logic(user_id: uuid.UUID):
    vps_list = await vps_logic.get_list_by_user_id(user_id=user_id)

    return success_response(
        VPSListResponse(
            vps=vps_list
        )
    )


async def buy_vps_logic():
    ...
