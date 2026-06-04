import os
from dotenv import load_dotenv

# โหลดค่าจากไฟล์ .env
load_dotenv()

class Config:
    # System
    ENV = os.getenv("JINX_ENV", "development")
    DEBUG = ENV == "development"
    
    # LLM Providers
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    PRIMARY_MODEL = os.getenv("PRIMARY_MODEL", "llama3")
    FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "gpt-3.5-turbo")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    # Storage & Database
    DB_TYPE = os.getenv("DB_TYPE", "sqlite") # หรือ 'postgresql' ในโปรดักชั่น
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Knowledge Base
    OBSIDIAN_VAULT_PATH = os.getenv("OBSIDIAN_VAULT_PATH", "data/knowledge")
    VECTOR_DB_PATH = "data/vector_store"

    @classmethod
    def validate(cls):
        """ตรวจสอบความพร้อมของ Config"""
        if cls.ENV == "production" and not cls.OPENAI_API_KEY:
            print("⚠️ Warning: Production mode without Fallback LLM Key")
