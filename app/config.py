from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    telegram_token: str

    openai_api_key: str
    openai_model: str = "gpt-4.1"
    tts_model: str = "gpt-4o-mini-tts"
    tts_voice: str = "alloy"
    whisper_model: str = "gpt-4o-transcribe"

    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: int

    database_url: str

    redis_host: str
    redis_port: int

    amplitude_api_key: str

    class Config:
        env_file = ".env"
        extra = "ignore"
        env_file_encoding = "utf-8"

    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
