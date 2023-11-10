import uuid
from fastapi import HTTPException, status, Request
from fastapi.security import HTTPBearer
from db.redis_db import get_redis_client
from schemas.token import RefreshToken, AccessToken
from schemas.users import UserCreate, UserLogin, UserBase
from services.authentication import get_payload_from_refresh_token, validate_token
from services.account_httpx_client import get_account_client
from services.notification_httpx_client import get_notification_client
from utils.token import create_access_token, create_refresh_token
from config.config import settings


class APIService:
    def __init__(self, redis_db, account_client, notification_client):
        """
        The __init__ function is called when the class is instantiated.
        It sets up the redis_db and account_client attributes for use in other functions.

        :param self: Represent the instance of the class
        :param redis_db: Create a connection to the redis database
        :param account_client: Create a client object that can be used to call the account service
        :return: A new instance of the class
        :doc-author: Trelent
        """
        self.redis_db = redis_db
        self.account_client = account_client
        self.notification_client = notification_client

    async def register_user(self, user: UserCreate, request: Request):

        account_response = await self.account_client.account_register(user, request)
        if account_response.status_code == 201:
            response = await self.notification_client.notification_register(email=user.email, request=request)
            if response.status_code == 200:
                data = {"user_info": response.json(),
                        'message': 'Registration successful. Please check your email to activate your account.'}
                return data
            else:
                raise HTTPException(status_code=response.status_code, detail=response.json())
        else:
            raise HTTPException(status_code=account_response.status_code, detail=account_response.json())

    async def login(self, form_data: UserLogin, request: Request):

        user_id = (await self.account_client.account_login(form_data, request)).json().get('user_id')
        access_token, refresh_token = await self.generate_tokens(user_id)
        return {"access": access_token, 'refresh': refresh_token}

    async def refresh_token(self, request: Request):
        """
        The refresh_token function is used to refresh the access token.
            It takes in a request object and returns a new access token.
            The function first extracts the payload from the request, validates it,
            then deletes it from redis database and generates new tokens for that user.

        :param self: Represent the instance of the class
        :param request: Request: Access the request object
        :return: A dictionary with two keys: access and refresh
        :doc-author: Trelent
        """
        payload = await self.extract_payload(request)
        await validate_token(payload)

        await self.get_jti(f"user_{payload.get('user_id')} || {payload.get('jti')}")

        await self.redis_db.delete(f"user_{payload.get('user_id')} || {payload.get('jti')}")

        user_id = payload.get('user_id')

        access_token, refresh_token = await self.generate_tokens(user_id)
        return {"access": access_token, 'refresh': refresh_token}

    async def log_out(self, payload: HTTPBearer):
        """
        The log_out function is used to log out a user.
        It takes in the payload of the token and checks if it exists in redis. If it does, then we delete that key from redis and return a message saying that the user has been signed out.

        :param self: Represent the instance of the class
        :param payload: HTTPBearer: Get the user_id and jti from the token
        :return: A message that the user has been signed out
        :doc-author: Trelent
        """
        await self.get_jti(f"user_{payload.get('user_id')} || {payload.get('jti')}")  # todo

        await self.redis_db.delete(f"user_{payload.get('user_id')} || {payload.get('jti')}")
        return {'message': 'User has been signed out'}

    async def generate_tokens(self, user_id: str):
        """
        The generate_tokens function is used to generate a new access token and refresh token for the user.
        The function takes in the user_id of the user as an argument, and returns a tuple containing both tokens.


        :param self: Represent the instance of the class
        :param user_id: Identify the user
        :return: A tuple of access_token and refresh_token
        :doc-author: Trelent
        """
        jti = uuid.uuid4().hex

        access_token = create_access_token(AccessToken(user_id=user_id, jti=jti))
        refresh_token = create_refresh_token(RefreshToken(user_id=user_id, jti=jti))

        await self.redis_db.set(f"user_{user_id} || {jti}", jti, ex=settings.REFRESH_TOKEN_LIFETIME)
        return access_token, refresh_token

    async def extract_payload(self, request: Request):
        """
        The extract_payload function is used to extract the payload from a refresh token.

        :param self: Access the class attributes and methods
        :param request: Request: Get the data from the request
        :return: A payload object
        :doc-author: Trelent
        """
        data = await request.json()
        token = data.get('token')
        return await get_payload_from_refresh_token(token)

    async def get_jti(self, key: str):
        jti = await self.redis_db.get(key)

        if not jti:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid token, please login again.')
        return jti


api_service = APIService(get_redis_client(), get_account_client(), get_notification_client())


def get_api_service():
    return api_service
