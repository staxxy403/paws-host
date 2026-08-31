from shared.models.responses import success_response
from database.logic import vps as vps_logic


async def get_list_vps_logic(user_id: int):
    await vps_logic.get_list_by_user_id(user_id=user_id)
