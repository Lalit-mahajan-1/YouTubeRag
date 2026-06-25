from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "YouTube RAG"
    
    FRONTEND_API_DEV: str
    FRONTEND_API_PROD: str
    DEBUG: bool = False
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 200 
    DATABASE_URL: str
    DIRECT_URL: str  # used for alembic migrations only
    GROQ_API_KEY: str
    PINECONE_API_KEY: str
    PINECONE_INDEX_NAME: str = "youtube-rag"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL: str = "llama-3.1-8b-instant"
    
    YOUTUBE_API_KEY: str
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 200

    RETRIEVAL_TOP_K: int = 4  
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()