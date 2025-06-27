# backend/reset_db.py
from sqlmodel import SQLModel
from app.db import engine
from app import models

# WARNING: this will erase all data in your asset table
SQLModel.metadata.drop_all(engine)
SQLModel.metadata.create_all(engine)
print("Dropped and re-created all tables.")
