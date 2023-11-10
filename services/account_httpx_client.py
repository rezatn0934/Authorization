from fastapi import Request, HTTPException
from schemas.users import UserCreate, UserLogin
from config.config import settings
import httpx


class AccountClient:
    register_url = settings.ACCOUNT_REGISTER_URL
    login_url = settings.ACCOUNT_LOGIN_URL

    async def _send_request(self, url: str, data: dict, request: Request):
        headers = {'correlation-id': request.state.correlation_id}
        async with httpx.AsyncClient(headers=headers) as client:
            try:
                response = await client.post(url, json=data)
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as exc:
                raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)

    async def account_register(self, user_info: UserCreate, request: Request):
        data = user_info.model_dump()
        return await self._send_request(self.register_url, data, request)

    async def account_login(self, user_info: UserLogin, request: Request):
        data = user_info.model_dump()
        return await self._send_request(self.login_url, data, request)


def get_account_client():
    return AccountClient()