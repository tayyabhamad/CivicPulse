import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from pythonjsonlogger.json import JsonFormatter

from app.routes.complaints import router as complaints_router
from app.routes.operations import lifespan
from app.routes.operations import router as operations_router


def configure_logging() -> logging.Logger:
    logger = logging.getLogger("civicpulse")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


logger = configure_logging()
app = FastAPI(title="CivicPulse API", version="0.1.0", lifespan=lifespan)
app.include_router(complaints_router)
app.include_router(operations_router)


@app.middleware("http")
async def request_context(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    started = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - started) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request_complete",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    return response


@app.get("/health", tags=["operations"])
async def health() -> dict[str, str]:
    """Liveness only: intentionally does not touch Postgres or Redis."""
    return {"status": "ok"}
