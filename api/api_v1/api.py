from fastapi import Depends, APIRouter, Request, status
from fastapi.security import HTTPBearer

from schemas.users import UserCreate, UserLogin, UserBase
from services.api_services import APIService, get_api_service
from services.authentication import get_access_jwt_aut

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(request: Request, user: UserCreate, api_service: APIService = Depends(get_api_service)):
    return await api_service.register_user(user, request)


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(request: Request, form_data: UserLogin, api_service: APIService = Depends(get_api_service)):
    return await api_service.login(form_data, request)


@router.post('/refresh', status_code=status.HTTP_201_CREATED)
async def refresh_token(request: Request, api_service: APIService = Depends(get_api_service)):
    """
    The refresh_token function is used to refresh the access token.
        The function takes in a request object and an api_service object, which is created using the get_api_service dependency.
        The function returns a response from the api service's refresh token method.

    :param request: Request: Pass the request object to the refresh_token function
    :param api_service: APIService: Get the apiservice object
    :return: The following:
    :doc-author: Trelent
    """

    return await api_service.refresh_token(request)


@router.post('/logout', status_code=status.HTTP_200_OK)
async def log_out(payload: HTTPBearer = Depends(get_access_jwt_aut()),
                  api_service: APIService = Depends(get_api_service)):
    """
    The log_out function is used to log out a user.

    :param payload: HTTPBearer: Get the access token from the http authorization header
    :param api_service: APIService: Get the api service object
    :return: A dictionary with the key 'message' and value 'logged out'
    :doc-author: Trelent
    """

    return await api_service.log_out(payload)
