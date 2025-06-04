

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:

    
    # API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    
    # Agent Configuration
    RESEARCH_AGENT_PORT: int = int(os.getenv("RESEARCH_AGENT_PORT", "8001"))
    ANALYTICS_AGENT_PORT: int = int(os.getenv("ANALYTICS_AGENT_PORT", "8002"))
    COORDINATOR_PORT: int = int(os.getenv("COORDINATOR_PORT", "8000"))
    
    # Agent URLs
    RESEARCH_AGENT_URL: str = os.getenv("RESEARCH_AGENT_URL", "http://localhost:8001")
    ANALYTICS_AGENT_URL: str = os.getenv("ANALYTICS_AGENT_URL", "http://localhost:8002")
    
    # Model Configuration
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # A2A Protocol Settings
    A2A_TIMEOUT: int = int(os.getenv("A2A_TIMEOUT", "30"))
    A2A_MAX_RETRIES: int = int(os.getenv("A2A_MAX_RETRIES", "3"))
    
    @classmethod
    def validate(cls) -> bool:
    
        required_keys = [
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY"
        ]
        
        missing_keys = []
        for key in required_keys:
            if not getattr(cls, key):
                missing_keys.append(key)
        
        if missing_keys:
            raise ValueError(f"Missing required environment variables: {missing_keys}")
        
        return True
    
    @classmethod
    def get_agent_card_template(cls, name: str, description: str, url: str, version: str = "1.0.0") -> dict:
    
        return {
            "name": name,
            "description": description,
            "url": url,
            "version": version,
            "capabilities": {
                "streaming": False,
                "pushNotifications": False
            }
        } 