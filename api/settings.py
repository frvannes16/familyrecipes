from os import path
from typing import Any, Optional, Dict
import sys

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


def _pytest_settings_override(_: BaseSettings) -> Dict[str, Any]:
    # If this code is running as a part of pytest, then we set DEBUG=True by default.
    if "pytest" in sys.modules:
        return {"debug": True}
    else:
        return {}


# Fields of this class are settings parsed by Pydantic from the .env file in your
# environment, and also from your environment variables. Environment variables take precedence.
# See https://pydantic-docs.helpmanual.io/usage/settings/#parsing-environment-variable-values
class Settings(BaseSettings):
    database_url: str
    database_name: str
    secret_key: str
    debug: bool
    google_client_id: Optional[str]
    google_client_secret: Optional[str]

    class Config:
        env_file = _dot_env_path()
        env_file_encoding = "utf-8"
        secrets_dir = "/var/run"

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                init_settings,
                _pytest_settings_override,  # Determine if pytest is running and set DEBUG=True
                env_settings,
                file_secret_settings,
            )


# Exported settings object.
settings = Settings()
