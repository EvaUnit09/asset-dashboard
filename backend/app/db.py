from sqlmodel import create_engine, Session
from .settings import Settings

settings = Settings()

engine = create_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
)

def get_session():
    with Session(engine) as session:
        yield session

        