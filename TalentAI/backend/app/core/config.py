from pydantic_settings import BaseSettings,SettingsConfigDict
class Settings(BaseSettings):


    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool

    HOST: str
    PORT: int

    DATABASE_URL: str

    # ==========================
    # Authentication
    # ==========================
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # ==========================
    # Resume Upload
    # ==========================
    UPLOAD_DIR: str

    # ==========================
    # Vector Database
    # ==========================
    FAISS_PATH: str = ""

    # ==========================
    # AI Models
    # ==========================
    EMBEDDING_MODEL_NAME: str = ""
    OLLAMA_MODEL_NAME: str = ""
    OLLAMA_BASE_URL: str = ""

    # Load values from .env
    model_config = SettingsConfigDict(
        env_file=r"C:\practice_vscode\TalentAI\backend\app\.env",
        extra="ignore"
    )


settings = Settings()
