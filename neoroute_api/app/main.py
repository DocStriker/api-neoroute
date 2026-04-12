import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, agent, cargas, states, geodata, controls, jobs
from app.models.db_models import init_db
from app.core.logging_config import setup_logging

import logging
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    setup_logging()
    init_db()
    yield
    logger.info("Shutting down...")

if os.getenv("ENV") == "aws":
    from mangum import Mangum

app = FastAPI(
    title="NeoRoute API",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(agent.router)
app.include_router(cargas.router)
app.include_router(states.router)
app.include_router(geodata.router)
app.include_router(controls.router)
app.include_router(jobs.router)

if os.getenv("ENV") == "aws":
    handler = Mangum(app)