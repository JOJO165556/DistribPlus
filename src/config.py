"""
Configuration globale du pipeline.
Charge les variables d'environnement de manière type-safe.
"""
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Paramètres applicatifs du projet."""

    # Base de données PostgreSQL
    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5436, alias="POSTGRES_PORT")
    postgres_db: str = Field(default="distribplus", alias="POSTGRES_DB")
    postgres_user: str = Field(default="distribplus", alias="POSTGRES_USER")
    postgres_password: str = Field(default="changeme", alias="POSTGRES_PASSWORD")

    # Chemins des données
    data_inbox: Path = Field(default=Path("./data/inbox"), alias="DATA_INBOX")
    data_rejects: Path = Field(default=Path("./data/rejects"), alias="DATA_REJECTS")
    data_archive: Path = Field(default=Path("./data/archive"), alias="DATA_ARCHIVE")

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        """URL de connexion standard SQLAlchemy / Psycopg."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
