from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str

    def DATABASE_URL_asyncpg(self, table_name: str):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{table_name}"

    def DATABASE_URL_psycopg(self, table_name: str):
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{table_name}"

    model_config = SettingsConfigDict(
        env_file=str(env_path),
        env_file_encoding="utf-8",
        extra="ignore")


settings = Settings()
