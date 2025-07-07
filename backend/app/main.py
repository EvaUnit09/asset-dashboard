from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from .db import engine
from .models import Asset
from .routers.assets import router as assets_router
from app.routers.sync import router as sync_router
from .routers.fun_queries import router as fun_queries_router
from fastapi.middleware.cors import CORSMiddleware
from .scheduler import sync_scheduler




@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    SQLModel.metadata.create_all(engine)
    sync_scheduler.start()
    yield
    # Shutdown
    sync_scheduler.stop()

app = FastAPI(
    title="Asset Management API",
    lifespan=lifespan,
)
origins = [
    "http://10.4.208.227",
    "http://asset-ny.worldwide.bbc.co.uk"
]

app.include_router(assets_router)
app.include_router(sync_router)
app.include_router(fun_queries_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)