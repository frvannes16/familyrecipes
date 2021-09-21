from os import path

from pydantic.env_settings import BaseSettings


def _dot_env_path() -> str:
    """Return the path of the .env file, even if the program is run from inside the api directory."""
    filename = ".env"

    if path.exists(filename):
        return filename
    elif path.exists("../" + filename) and path.abspath(path.curdir).endswith("api"):
        # use dotenv file from parent directory. We assume we are in the "api" directory.
        return f"../{filename}"
    else:
        print("Could not find .env file, using environment variables.")
        return filename


# Fields of this class are settings parsed by Pydantic from the .env file in your
# environment, and also from your environment variables. Environment variables take precedence.
# See https://pydantic-docs.helpmanual.io/usage/settings/#parsing-environment-variable-values
class Settings(BaseSettings):
    database_url: str
    database_name: str

    class Config:
        env_file = _dot_env_path()
        env_file_encoding = "utf-8"
        secrets_dir = "/var/run"


# Exported settings object.
settings = Settings()
