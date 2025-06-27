from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlmodel import SQLModel, select, Session
from .db import engine, get_session
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
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app.include_router(assets_router)
app.include_router(sync_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)