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
    postgres_password: str
        
settings = Settings()  # type: ignore
print(f"DATABASE_URL: {settings.database_url}")
print(f"config loaded from: {settings.model_config.get('env_file')}")