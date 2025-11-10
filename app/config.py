from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # Database Configuration
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "fastapi_db"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: str = "5432"
    
    # Exchange Rate Configuration
    exchange_rate_api_key: str = ""
    exchange_rate_api_url: str = "https://v6.exchangerate-api.com/v6"

    # Application Configuration
    default_currency: str = "USD"
    app_name: str = "Multi-Currency Invoice Analytics API"
    app_version: str = "1.0.0"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()

