from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            Path(__file__).parent.parent / ".env",
            Path(__file__).parent.parent / ".env.local"
            ),
        env_file_encoding="utf-8",
        extra='ignore'
    )
    
    
    database_url: str
    snipeit_api_url: str
    snipeit_token: str
    requests_ca_bundle: str | None = None
    echo_sql: bool = False
    postgres_password: str | None = None
        
settings = Settings()  # type: ignore