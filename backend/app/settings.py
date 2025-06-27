from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    snipeit_api_url: str
    snipeit_token: str
    echo_sql: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
settings = Settings()