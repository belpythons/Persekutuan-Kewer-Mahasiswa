import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Konfigurasi Environment Microservice AI
    """
    APP_NAME: str = "KIDECO Fuel Ratio AI Service"
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    # PostgreSQL Configuration
    POSTGRES_USER: str = "postgres.nxgurgphgoelraasauqt"
    POSTGRES_PASSWORD: str = "SiG8AHzB5E4BxtV2"
    POSTGRES_HOST: str = "aws-0-ap-southeast-1.pooler.supabase.com"
    POSTGRES_PORT: int = 6543
    POSTGRES_DB: str = "postgres"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
