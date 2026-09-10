import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    gemini_embedding_model: str = "models/text-embedding-004"
    chroma_persist_dir: str = "./chroma_data"
    cors_origins_raw: str = "http://localhost:5173"
    chunk_size: int = 900
    chunk_overlap: int = 150
    top_k: int = 6

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }

    def __init__(self, **kwargs):
        import os
        if "CORS_ORIGINS" in os.environ and "cors_origins_raw" not in kwargs:
            kwargs["cors_origins_raw"] = os.environ["CORS_ORIGINS"]
        super().__init__(**kwargs)

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]


settings = Settings()