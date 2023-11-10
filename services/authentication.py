from typing import Any
import jwt

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from utils.token import decode_token
from db.redis_db import get_redis_client

redis = get_redis_client()


async def get_payload_from_access_token(token):
    try:
        access_token = token.split(' ')[1]
        payload = decode_token(access_token)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Expired access token")
    except jwt.InvalidSignatureError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid access token")


async def get_payload_from_refresh_token(token):
    try:
        payload = decode_token(token)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Expired refresh token")
    except jwt.InvalidSignatureError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


async def validate_token(payload: dict) -> Any:
    jti = payload.get('jti')
    user_id = payload.get('user_id')
    result = await redis.get(f"user_{user_id} || {jti}")
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Invalid token, please login again.')


class JWTAuthentication(HTTPBearer):
    authentication_header_prefix = 'Token'
    authentication_header_name = 'Authorization'

    def authenticate_header(self, request: Request):
        return self.authentication_header_prefix

    def __init__(self, auto_error: bool = True):
        super(JWTAuthentication, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):

        authorization_header = await self.get_authorization_header(request)
        if not authorization_header:
            return None

        self.check_prefix(authorization_header)
        payload = await get_payload_from_access_token(authorization_header)
        await validate_token(payload)
        return payload

    async def get_authorization_header(self, request):
        authorization_header = request.headers.get(self.authentication_header_name)
        if not authorization_header:
            return None
        return authorization_header

    def check_prefix(self, authorization_header):
        prefix = authorization_header.split(' ')[0]
        if prefix != self.authentication_header_prefix:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid authentication scheme")


access_jwt_auth = JWTAuthentication()


def get_access_jwt_aut():
    return access_jwt_auth
