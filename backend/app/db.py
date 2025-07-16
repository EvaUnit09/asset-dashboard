from sqlmodel import create_engine, Session
from .settings import settings

# Main assets database engine
engine = create_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
)

# Separate users database engine
users_engine = create_engine(
    settings.users_database_url,
    echo=False,
    pool_pre_ping=True,
)

def get_session():
    with Session(engine) as session:
        yield session

def get_users_session():
    with Session(users_engine) as session:
        yield session

        