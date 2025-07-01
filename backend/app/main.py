from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from .db import engine
from .models import Asset
from .routers.assets import router as assets_router
from app.routers.sync import router as sync_router
from fastapi.middleware.cors import CORSMiddleware




@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)