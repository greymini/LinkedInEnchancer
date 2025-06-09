import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings loaded from environment variables"""
    
    GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")
    APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")
    
    # Streamlit Configuration
    STREAMLIT_SERVER_PORT = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
    
    # Memory Storage
    MEMORY_STORE_PATH = os.getenv("MEMORY_STORE_PATH", "./data/memory_store")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Model Configuration
    DEFAULT_TEMPERATURE = 0.7
    MAX_OUTPUT_TOKENS = 2048
    
    @classmethod
    def validate_settings(cls):
        """Validate that all required settings are present"""
        required_settings = [
            ("GOOGLE_GEMINI_API_KEY", cls.GEMINI_API_KEY),
            ("APIFY_API_TOKEN", cls.APIFY_API_TOKEN)
        ]
        
        missing_settings = []
        for name, value in required_settings:
            if not value:
                missing_settings.append(name)
        
        if missing_settings:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_settings)}")
        
        return True

# Create global settings instance
settings = Settings() 