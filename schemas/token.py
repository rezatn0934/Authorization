import datetime
from pydantic import BaseModel
from config.config import settings

ACCESS_TOKEN_LIFETIME = settings.ACCESS_TOKEN_LIFETIME
REFRESH_TOKEN_LIFETIME = settings.REFRESH_TOKEN_LIFETIME


class Token(BaseModel):
    """
    Token Model
    """
    user_id: str
    jti: str


class AccessToken(Token):
    token_type: str = 'access'


class RefreshToken(Token):
    token_type: str = 'refresh'

