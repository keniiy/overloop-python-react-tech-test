import os
from typing import Optional


class Settings:
    """Application configuration management"""
    
    # Database Configuration
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///database.db')
    DATABASE_ECHO: bool = os.getenv('DATABASE_ECHO', 'true').lower() == 'true'
    
    # Flask Configuration
    FLASK_ENV: str = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG: bool = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # API Configuration
    API_HOST: str = os.getenv('API_HOST', '0.0.0.0')
    API_PORT: int = int(os.getenv('API_PORT', '5000'))
    
    # CORS Configuration
    CORS_ORIGINS: str = os.getenv('CORS_ORIGINS', '*')
    
    # Testing Configuration
    TESTING: bool = os.getenv('TESTING', 'false').lower() == 'true'
    TEST_DATABASE_URL: str = os.getenv('TEST_DATABASE_URL', 'sqlite:///:memory:')
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get appropriate database URL based on environment"""
        if cls.TESTING:
            return cls.TEST_DATABASE_URL
        return cls.DATABASE_URL


# Global settings instance
settings = Settings()