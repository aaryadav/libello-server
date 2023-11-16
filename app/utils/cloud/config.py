from pathlib import Path
from inspect import signature
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List
from pathlib import Path

from pydantic.main import BaseModel
from .errors import AutherizeGoogleClient

from botocore.config import Config

import os


class GoogleDriveConfig(BaseSettings):
    CLIENT_ID_JSON: str
    SCOPES: List[str]
    STORAGE_JSON: Path

    class Config:
        case_sensitive = True

    @validator("STORAGE_JSON")
    def validate_name(cls, v):
        # Convert string to Path if not None
        v_path = Path(v) if v else Path(
            "/home/aaryaman/mycode/libello-server/storage.json")

        if v_path.exists():
            return v_path
        else:
            raise AutherizeGoogleClient(
                "File for authorizing does not exist at the path: {0}".format(v_path))


class S3Config(BaseSettings):
    AWS_ACCESS_KEY_ID:                  str = Field(
        None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY:              str = Field(
        None, env="AWS_SECRET_ACCESS_KEY")
    AWS_DEFAULT_REGION:                 str = Field(
        ..., env="AWS_DEFAULT_REGION")
    AWS_CONFIG_FILE:                    str = Field(
        "~/.aws/config", env="AWS_CONFIG_FILE")
    AWS_SHARED_CREDENTIALS_FILE:        str = Field(
        "~/.aws/credentials", env="AWS_SHARED_CREDENTIALS_FILE")

    class Config:
        case_sensitive = True
