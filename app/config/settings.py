from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # SMTP Configuration
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str
    smtp_password: str
    smtp_use_tls: bool = True
    
    # Default Email Settings
    default_from_email: str
    default_from_name: str = "Email Service"
    
    # API Configuration
    api_title: str = "Email Service API"
    api_description: str = "A microservice for sending emails"
    api_version: str = "1.0.0"
    
    # Application Settings
    debug: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
