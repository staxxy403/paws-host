from typing import Any

from pydantic import BaseModel

class APIResponse(BaseModel):
    ok: bool
    error: str | None
    data: Any

def success_response(data: Any = 'OK') -> dict:
    return APIResponse(ok=True, data=data, error=None).model_dump()
