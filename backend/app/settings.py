from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env",
        env_file_encoding="utf-8"
    )
    
    database_url: str
    snipeit_api_url: str
    snipeit_token: str
    requests_ca_bundle: str | None = None
    echo_sql: bool = False
        
settings = Settings()  # type: ignore