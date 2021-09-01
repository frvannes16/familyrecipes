from pydantic.env_settings import BaseSettings

# Fields of this class are settings parsed by Pydantic from the .env file in your
# environment, and also from your environment variables. Environment variables take precedence.
# See https://pydantic-docs.helpmanual.io/usage/settings/#parsing-environment-variable-values
class Settings(BaseSettings):
    database_url: str
    database_name: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        secrets_dir = "/var/run"


# Exported settings object.
settings = Settings()
