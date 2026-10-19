from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "FlyRank Image Relevance Engine"
    database_url: str = "sqlite:///./image_relevance.db"
    vision_provider: str = "local"
    embedding_provider: str = "local"

    # OpenRouter vision configuration
    openrouter_api_key: str = ""
    openrouter_model: str = "openrouter/free"
    openrouter_fallback_models: str = ""

    # Retained for backward compatibility
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    ollama_base_url: str = "http://localhost:11434"
    ollama_vision_model: str = "llava"
    ollama_embedding_model: str = "all-minilm"
    vision_confidence_threshold: float = 0.60
    match_similarity_threshold: float = 0.18
    max_batch_retries: int = 2
    estimated_vision_call_cost_usd: float = 0.0
    estimated_embedding_call_cost_usd: float = 0.0
    asset_dir: str = "assets/demo"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
