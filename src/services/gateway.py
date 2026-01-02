from typing import Optional, Union

import httpx
from fastapi import HTTPException

from src.config import config
from src.logconf import opt_logger as log
from src.models import User, Profile

logger = log.setup_logger('gateway service')


class GatewayService:
    def __init__(self, host: str, port: int):
        self.gateway_url = f'http://{host}:{port}'
        self.session: Optional["httpx.AsyncClient"] = None

    async def __aenter__(self):
        self.connect()
        return self

    async def __aexit__(self, *args):
        await self.close()

    def connect(self) -> None:
        """Подключение к серверу"""
        self.session = httpx.AsyncClient()

    async def close(self) -> None:
        if self.session:
            await self.session.aclose()

    async def _execute_request(self, method_name: str, CRUD: str, *args, **kwargs) -> dict:
        """ Исполняет различные CRUD запросы """
        method = getattr(self, f"_{CRUD}_{method_name}", None)

        if method is None:
            raise AttributeError(f'{CRUD} метод {method_name} не существует')

        return await method(*args, **kwargs)


    async def get(self, method_name: str, *args, **kwargs):
        """ GET запросы к внешнему серверу """
        return await self._execute_request(method_name, 'get', *args, **kwargs)

    async def post(self, method_name: str, *args, **kwargs):
        """POST запросы к внешнему серверу"""
        return await self._execute_request(method_name, 'post', *args, **kwargs)

    async def put(self, method_name: str, *args, **kwargs):
        """PUT запросы к внешнему серверу"""
        return await self._execute_request(method_name, 'put', *args, **kwargs)

    # GET функции
    async def _get_check_user_exists(self, user_id: int):
        """ Проверка существования пользователя """
        url = f'{self.gateway_url}/api/users?user_id={user_id}'
        resp = await self.session.get(url=url)
        if resp.status_code == 200:
            return resp.json()
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    async def _get_nickname_exists(self, nickname: str) -> httpx.Response:
        url = f'{self.gateway_url}/api/nicknames?nickname={nickname}'
        resp = await self.session.get(url=url)
        if resp.status_code == 200:
            return resp.json()
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    async def _get_user_data(self, user_id: int, target: str) -> httpx.Response:
        """ Запращивает данные о пользователе по опреденному критерию """
        url = f'{self.gateway_url}/api/users?user_id={user_id}&target_field={target}'
        resp = await self.session.get(url=url)
        if resp.status_code == 200:
            return resp.json()
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    async def _get_payment_data(self, user_id: int) -> dict:
        url = f'{self.gateway_url}/api/payment_data?user_id={user_id}'
        resp = await self.session.get(url=url)
        if resp.status_code == 200:
            return resp.json()
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    async def _get_due_to(self, user_id: int) -> httpx.Response:
        url = f'{self.gateway_url}/api/due_to?user_id={user_id}'
        resp = await self.session.get(url=url)
        if resp.status_code == 200:
            return resp.json()
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    async def _get_yookassa_link(self, user_id: int):
        url = f'{self.gateway_url}/api/yookassa_link?user_id={user_id}'
        resp = await self.session.get(url=url)
        if resp.status_code == 200:
            return resp.json()
        raise HTTPException(status_code=500, detail='Server Internal Error')

    # POST функции
    async def _post_add_user(self, user_data: User):
        url = f'{self.gateway_url}/api/users'
        headers = {"Content-Type": "application/json"}

        resp = await self.session.post(
            url=url,
            headers=headers,
            content=user_data.model_dump_json(),
            timeout=10.0
        )
        if resp.status_code == 200:
            return resp.json()
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    async def _post_activate_subscription(self, user_id: int):
        url = f'{self.gateway_url}/api/toggle_sub'
        headers = {"Content-Type": "application/json"}
        data = {'user_id': user_id, 'activate': True}
        resp = await self.session.post(
            url=url,
            headers=headers,
            json=data,
            timeout=10.0
        )

        if resp.status_code == 200: return

        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    async def _post_deactivate_subscription(self, user_id: int):
        url = f'{self.gateway_url}/api/toggle_sub'
        headers = {"Content-Type": "application/json"}
        data = {'user_id': user_id, 'activate': False}
        resp = await self.session.post(
            url=url,
            headers=headers,
            json=data,
            timeout=10.0
        )

        if resp.status_code == 200: return

        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    # PUT функции
    async def _put_update_profile(self, new_data: Union[User, Profile]):

        url = f'{self.gateway_url}/api/update_profile'
        response = await self.session.put(
            url=url,
            headers={'content-type': 'application/json'},
            content=new_data.model_dump_json(),
            timeout=10.0
        )
        response.raise_for_status()
        return response


gateway_service = GatewayService(config.gateway.host, config.gateway.port)
