from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ASYNC_DATABASE_URL: str 
    SYNC_DATABASE_URL: str
    secret_key: str
    access_token_expire_minutes:int
    algorithm:str
    gemini_key:str

    # Database URLs
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


 


settings = Settings() #type:ignore
