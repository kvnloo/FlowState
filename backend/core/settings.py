from dataclasses import dataclass
from typing import Dict, Optional
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class ShimmerConfig:
    base_url: str
    client_id: str
    client_secret: str

@dataclass
class Config:
    # Shimmer configuration
    shimmer: ShimmerConfig = ShimmerConfig(
        base_url=os.getenv("SHIMMER_BASE_URL", "http://localhost:8083"),
        client_id=os.getenv("SHIMMER_CLIENT_ID", ""),
        client_secret=os.getenv("SHIMMER_CLIENT_SECRET", "")
    )
    
    # Database configuration
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./flowstate.db")
    
    # API configuration
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    
    # Data storage paths
    data_dir: Path = Path(os.getenv("DATA_DIR", "./data"))
    
    # Feature flags
    enable_gut_microbiome_analysis: bool = os.getenv("ENABLE_GUT_MICROBIOME", "false").lower() == "true"
    enable_eye_tracking: bool = os.getenv("ENABLE_EYE_TRACKING", "false").lower() == "true"
    enable_kovaak_integration: bool = os.getenv("ENABLE_KOVAAK", "false").lower() == "true"

# Create a global config instance
config = Config()
