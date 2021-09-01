from pydantic.env_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        secrets_dir = "/var/run"


# Exported settings object.
settings = Settings()
