"""
Configuration management for Wafer Detection Agent.
Centralizes all application settings.
"""
from typing import List
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./wafer_analysis.db"
    
    # Model Paths
    MODEL_PATH_TORCH: str = "k_cross_CNN.pt"
    MODEL_PATH_VIT: str = "ViT_Wafer_Defect.h5"
    MODEL_PATH_EXT: str = "my_model.weights.h5"
    
    # Model Configuration
    MODEL_DEVICE: str = "cpu"  # or "cuda" if available
    ENABLE_MODEL_CACHING: bool = True
    
    # Analytics Defaults
    SPC_DEFAULT_DAYS: int = 30
    SPC_CONTROL_LIMIT_SIGMA: int = 3
    TREND_DEFAULT_DAYS: int = 30
    
    # Detection Thresholds
    CONFIDENCE_THRESHOLD_LOW: float = 0.25
    CONFIDENCE_THRESHOLD_MEDIUM: float = 0.50
    CONFIDENCE_THRESHOLD_HIGH: float = 0.75
    DEFECT_PROBABILITY_SIGNIFICANT: float = 0.10
    DEFECT_PROBABILITY_MINOR: float = 0.05
    
    # Image Processing
    IMAGE_SIZE_HEIGHT: int = 56
    IMAGE_SIZE_WIDTH: int = 56
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = ["*"]
    RELOAD: bool = True
    
    # Email Configuration (optional)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/wafer_detection.log"
    LOG_MAX_BYTES: int = 10_000_000  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }


# Global settings instance
settings = Settings()
