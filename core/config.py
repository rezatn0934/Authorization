from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGO_URI: str
    REDIS_URI: str
    ACCESS_TOKEN_LIFETIME: int
    REFRESH_TOKEN_LIFETIME: int
    SECRET_KEY: str
    ALGORITHM: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
