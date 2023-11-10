import datetime
import jwt

from config.config import settings
from schemas.token import AccessToken, RefreshToken

ACCESS_TOKEN_LIFETIME = settings.ACCESS_TOKEN_LIFETIME
REFRESH_TOKEN_LIFETIME = settings.REFRESH_TOKEN_LIFETIME


def create_access_token(payload: AccessToken):
    payload = payload.model_dump()
    payload['iat'] = datetime.datetime.utcnow()
    payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=ACCESS_TOKEN_LIFETIME)

    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(payload: RefreshToken):
    payload = payload.model_dump()
    payload['iat'] = datetime.datetime.utcnow()
    payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=REFRESH_TOKEN_LIFETIME)
    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str):
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    return payload
