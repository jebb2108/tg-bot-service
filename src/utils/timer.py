from datetime import datetime, timedelta, timezone
from typing import Optional, Union

from src.config import config

DEFAULT_TZ = config.tzinfo

def get_current_time(
        delta: timedelta = timedelta(0),
        as_string: bool = False,
        tz_aware: bool = False,
        tz: Optional[timezone] = None
) -> Union[datetime, str]:
    """
    Получить текущее время в различных форматах.

    Args:
        delta: Смещение времени от текущего момента (по умолчанию 0)
        as_string: Если True, вернуть строку, иначе объект datetime
        tz_aware: Если True, вернуть время с часовым поясом
        tz: Часовой пояс для aware времени (по умолчанию используется DEFAULT_TZ)

    Returns:
        datetime или строку в зависимости от параметра as_string
"""

    # Используем переданный часовой пояс или глобальный по умолчанию
    target_tz = tz if tz is not None else DEFAULT_TZ

    # Получаем текущее время в UTC (aware)
    now_utc = datetime.now(timezone.utc)

    # Добавляем смещение
    target_time = now_utc + delta


    if tz_aware:
        # Конвертируем в указанный часовой пояс
        target_time = target_time.astimezone(target_tz)

    else:
        # Конвертируем в нужный часовой пояс
        local_time = target_time.astimezone(target_tz)
        # Убираем информацию о часовом поясе (делаем naive)
        target_time = local_time.replace(tzinfo=None)


    if as_string:
        return target_time.isoformat()

    return target_time


# Вспомогательные функции для удобства
def get_current_datetime(delta: timedelta = timedelta(0)) -> datetime:
    """Текущее время + delta в виде naive объекта datetime"""
    return get_current_time(delta=delta, as_string=False, tz_aware=False)


def get_current_naive_str(delta: timedelta = timedelta(0)) -> str:
    """Текущее время + delta в виде строки naive"""
    return get_current_time(delta=delta, as_string=True, tz_aware=False)


def get_current_aware_str(delta: timedelta = timedelta(0)) -> str:
    """Текущее время + delta в виде строки aware"""
    return get_current_time(delta=delta, as_string=True, tz_aware=True)


def get_current_aware_datetime(delta: timedelta = timedelta(0)) -> datetime:
    """Текущее время + delta в виде aware объекта datetime"""
    return get_current_time(delta=delta, as_string=False, tz_aware=True)