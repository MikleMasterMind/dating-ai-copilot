from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import init_db
from app.routes import health


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialize the database on application startup."""
    await init_db()
    yield


def create_app() -> FastAPI:
    """Application factory: create and configure the FastAPI app."""
    app = FastAPI(lifespan=lifespan)
    app.include_router(health.router)
    return app


app = create_app()
