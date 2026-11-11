from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.inn import is_valid_inn
from app.models import TrackedInn, User


class ServiceError(ValueError):
    pass


async def get_or_create_user(session: AsyncSession, telegram_id: int) -> User:
    user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
    if user is None:
        user = User(telegram_id=telegram_id, timezone=settings.default_timezone)
        session.add(user)
        await session.flush()
    return user


async def add_inn(session: AsyncSession, telegram_id: int, inn: str) -> None:
    inn = inn.strip()
    if not is_valid_inn(inn):
        raise ServiceError("ИНН некорректен: укажите 10 или 12 цифр с верными контрольными разрядами.")
    user = await get_or_create_user(session, telegram_id)
    existing = await session.scalar(
        select(TrackedInn).where(TrackedInn.user_id == user.id, TrackedInn.inn == inn)
    )
    if existing:
        raise ServiceError("Этот ИНН уже есть в вашем списке.")
    from sqlalchemy import func
    count = await session.scalar(
        select(func.count()).select_from(TrackedInn).where(TrackedInn.user_id == user.id)
    )
    if count >= settings.max_inns_per_user:
        raise ServiceError(f"Лимит — {settings.max_inns_per_user} ИНН на пользователя.")
    session.add(TrackedInn(user_id=user.id, inn=inn))


async def remove_inn(session: AsyncSession, telegram_id: int, inn: str) -> bool:
    user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
    if user is None:
        return False
    item = await session.scalar(
        select(TrackedInn).where(TrackedInn.user_id == user.id, TrackedInn.inn == inn.strip())
    )
    if item is None:
        return False
    await session.delete(item)
    return True


async def list_inns(session: AsyncSession, telegram_id: int) -> list[str]:
    user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
    if user is None:
        return []
    rows = await session.scalars(
        select(TrackedInn.inn).where(TrackedInn.user_id == user.id).order_by(TrackedInn.inn)
    )
    return list(rows.all())
