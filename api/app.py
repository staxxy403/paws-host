import logging
from contextlib import asynccontextmanager

from arq import create_pool
from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from api.routes import routes_router
from shared.configs.redis import arq_redis_settings
from shared.models import APIResponse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

logger = logging.getLogger(__name__)

main_router = APIRouter(prefix='/api/v1')
main_router.include_router(routes_router)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.arq_pool = await create_pool(arq_redis_settings)
    yield
    await app.state.arq_pool.close()

app = FastAPI(lifespan=lifespan)
app.include_router(main_router)


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict):
        error_msg = exc.detail.get("message", "unknown_error")
        error_data = exc.detail.get("data", None)
    else:
        error_msg = str(exc.detail)
        error_data = None

    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse(
            ok=False,
            error=error_msg,
            data=error_data
        ).model_dump()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=APIResponse(
            ok=False,
            error='validation_error',
            data=exc.errors()
        ).model_dump()
    )


@app.exception_handler(Exception)
async def universal_exception_handler(request: Request, exc: Exception):
    logger.error('Critical unhandled crash', exc_info=exc)

    return JSONResponse(
        status_code=500,
        content=APIResponse(ok=False, error='Internal server error, check logs', data=None).model_dump()
    )
