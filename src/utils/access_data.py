from datetime import datetime

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from src.dependencies import get_gateway
from src.exc import StorageDataException
from src.utils.timer import get_current_naive_str, get_current_datetime


class MultiSelection(StatesGroup):
    waiting_nickname = State()
    waiting_language = State()
    waiting_fluency = State()
    waiting_topic = State()
    waiting_intro = State()
    ended_change = State()

class DataStorage:

    async def get_storage_data(
        self, user_id: int, state: FSMContext, renew: bool = False
    ) -> dict:
        """Достаем нужные данные о пользователе"""

        # При renew = True обновляет данные
        if renew: await state.clear()

        s_data = await state.get_data()

        # Проверяем наличие необходимых ключей
        keys = ["user_id", "first_name", "is_active", "lang_code"]
        if all(s_data.get(key, False) for key in keys):
            return s_data

        # Если данных нет в Redis, получаем из базы и сохраняем в Redis
        user_data = await self.set_user_info(user_id)
        if not user_data:
            raise StorageDataException

        await state.update_data(user_data)
        return user_data

    @staticmethod
    async def set_user_info(user_id: int) -> dict:
        """
        Гарантирует, что машина состояния
        имеет все данные о пользователе
        """
        gateway = await get_gateway()
        # Отправляем запрос в БД на получение информации
        async with gateway:
            # Базовая информация о пользователе
            user_info = await gateway.get(
                'user_data', user_id, target='users'
            )
            # Платежные данные о пользователе
            payment_info = await gateway.get(
                'payment_data', user_id
            )
            # Доп. регистрация о пользователе
            profile_info = await gateway.get(
                'user_data', user_id, target='profiles'
            )

        if not user_info:
            return {}

        result = {
            "user_id": user_id,
            "username": user_info["username"],
            "first_name": user_info["first_name"],
            "language": user_info["language"],
            "fluency": user_info["fluency"],
            "topics": ', '.join(user_info["topics"]),
            "camefrom": user_info["camefrom"],
            "lang_code": user_info["lang_code"],
            "is_active": payment_info.get("is_active", False),
            "due_to": payment_info.get("until", lambda: get_current_naive_str)
        }

        if profile_info and not profile_info.get('error', False):
            birthday = profile_info["birthday"]

            if isinstance(birthday, str):
                birthday = datetime.fromisoformat(birthday)


            result.update(
                {
                    "birthday": profile_info["birthday"],
                    "nickname": profile_info["nickname"],
                    "email": profile_info["email"],
                    "gender": profile_info["gender"],
                    "dating": profile_info["dating"],
                    "intro": profile_info['intro'],
                    "status": profile_info["status"],
                    "age": (get_current_datetime()-birthday).days//365
                }
            )

        return result




data_storage = DataStorage()