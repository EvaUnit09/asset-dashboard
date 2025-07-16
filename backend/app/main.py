from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from .db import engine, users_engine
from .models import Asset, User
from .routers.assets import router as assets_router
from app.routers.sync import router as sync_router
from .routers.fun_queries import router as fun_queries_router
from .routers.users import router as users_router
from fastapi.middleware.cors import CORSMiddleware
from .scheduler import sync_scheduler




@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # Create tables for main assets database
    SQLModel.metadata.create_all(engine)
    # Create tables for users database  
    SQLModel.metadata.create_all(users_engine)
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
    "http://asset-ny.worldwide.bbc.co.uk",
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # Alternative dev port
    "http://127.0.0.1:5173",  # Alternative localhost format
    "http://127.0.0.1:3000"   # Alternative localhost format
]

app.include_router(assets_router)
app.include_router(sync_router)
app.include_router(fun_queries_router)
app.include_router(users_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)