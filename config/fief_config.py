from fastapi.security import OAuth2AuthorizationCodeBearer
from fief_client import FiefAccessTokenInfo, FiefAsync, FiefUserInfo
from fief_client.integrations.fastapi import FiefAuth

from config.settings import *

fief = FiefAsync(
    settings.fief_base_url,
    settings.fief_client_id,
    settings.fief_client_secret,
)

scheme = OAuth2AuthorizationCodeBearer(
    settings.fief_authorize_endpoint,
    settings.fief_token_endpoint,
    scopes=settings.get_fief_scopes,
    auto_error=False,
)

auth = FiefAuth(fief, scheme)
