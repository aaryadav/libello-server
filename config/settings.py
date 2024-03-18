from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    fief_base_url: str
    fief_client_id: str
    fief_client_secret: str
    fief_authorize_endpoint: str
    fief_token_endpoint: str
    fief_scopes: str
    redis_host: str
    redis_port: int
    redis_db: int
    
    r2_token_value: str
    r2_access_id_key: str
    r2_secret_access_key: str
    r2_endpoint: str

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

    @property
    def get_fief_scopes(self) -> dict:
        return {scope: "Description for " + scope for scope in self.fief_scopes.split()}

settings = Settings()