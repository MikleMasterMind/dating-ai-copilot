from fastapi import FastAPI

from app.routes import health


def create_app() -> FastAPI:
    """Application factory: create and configure the FastAPI app."""
    app = FastAPI()
    app.include_router(health.router)
    return app


app = create_app()
