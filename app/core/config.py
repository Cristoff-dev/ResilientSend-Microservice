# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "ResilientSend-Microservice"
    
    # Upstash Redis Connection String
    REDIS_URL: str = "redis://localhost:6379"
    IDEMPOTENCY_EXPIRE_SECONDS: int = 86400

    # Primary Email Provider (Resend)
    RESEND_API_KEY: str
    
    # Fallback Email Provider (SendGrid)
    SENDGRID_API_KEY: str
    
    # SMS Provider (Twilio)
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_FROM_NUMBER: str

    # Pydantic v2 configuration standard
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore" # Ignores other OS-level environment variables
    )

settings = Settings()