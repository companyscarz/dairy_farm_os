import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "FarmOS")
    database_url: str = os.getenv("DATABASE_URL")
    secret_key: str = os.getenv("SECRET_KEY", "")
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "7070"))
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    session_cookie_secure: bool = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    db_min_size: int = int(os.getenv("DB_MIN_SIZE", "2"))
    db_max_size: int = int(os.getenv("DB_MAX_SIZE", "10"))

    def validate(self) -> None:
        if not self.secret_key or self.secret_key == "replace-with-a-long-random-secret":
            if not self.debug:
                raise RuntimeError("SECRET_KEY must be configured in production.")
        if not self.database_url.startswith(("postgresql://", "postgres://")):
            raise RuntimeError("This application requires PostgreSQL via DATABASE_URL.")


settings = Settings()
