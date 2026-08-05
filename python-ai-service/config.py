import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Konfigurasi Environment Microservice AI (Supabase Cloud PostgreSQL + Local Fallback)
    """
    APP_NAME: str = "KIDECO Fuel Ratio AI Service"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Supabase Configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://nxgurgphgoelraasauqt.supabase.co")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "sb_publishable_iRCaHzS3-hjk9id4GjIRKg_oMx-UrrP")
    SUPABASE_PROJECT_ID: str = os.getenv("SUPABASE_PROJECT_ID", "nxgurgphgoelraasauqt")
    
    # PostgreSQL / Supabase Connection Pool
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "db.nxgurgphgoelraasauqt.supabase.co")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "postgres")
    
    @property
    def DATABASE_URL(self) -> str:
        if self.POSTGRES_PASSWORD:
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        # Direct Supabase PostgreSQL URL if password supplied in env
        return f"postgresql://{self.POSTGRES_USER}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
