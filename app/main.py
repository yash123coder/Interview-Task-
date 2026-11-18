
from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.api.routes.internal import router as internal_router
from app.core.config import settings
from app.db.database import Base, engine

# Import models so SQLAlchemy registers all tables.
from app.db import models

from app.api.routes.leads import router as leads_router
from app.api.routes.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    Base.metadata.create_all(bind=engine)

    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "REST API for AI-powered lead management, "
        "automation and agent integration."
    ),
    lifespan=lifespan
)


app.include_router(health_router)
app.include_router(leads_router, prefix="/api")
app.include_router(internal_router)


@app.get("/")
def root():

    return {
        "message": "Welcome to AI Lead Management System",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }
