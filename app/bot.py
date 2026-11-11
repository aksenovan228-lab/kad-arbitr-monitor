import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from sqlalchemy import select, text

from app.config import settings
from app.db import SessionLocal, engine
from app.models import User
from app.services import add_inn, list_inns, remove_inn, ServiceError

dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message) -> None:
    async with SessionLocal() as session:
        async with session.begin():
            user = await session.scalar(select(User).where(User.telegram_id == message.from_user.id))
            if user is None:
                user = User(telegram_id=message.from_user.id, timezone=settings.default_timezone)
                session.add(user)
            user.consent_version = "mvp-1"
            from datetime import datetime, timezone
            user.consented_at = datetime.now(timezone.utc)
    await message.answer(
        "Бот подготовлен для мониторинга арбитражных дел по ИНН.\n"
        "Нажимая /start, вы соглашаетесь на обработку введённых данных для этой функции. "
        "Не отправляйте чужие ИНН без законного основания.\n\n"
        "Команды: /add ИНН, /remove ИНН, /list, /settings. "
        "Доступ к КАД пока отключён до подтверждения разрешённого способа."
    )


@dp.message(Command("add"))
async def add_handler(message: Message) -> None:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("Формат: /add 7707083893")
        return
    try:
        async with SessionLocal() as session:
            async with session.begin():
                await add_inn(session, message.from_user.id, parts[1])
        await message.answer("ИНН добавлен.")
    except ServiceError as exc:
        await message.answer(str(exc))


@dp.message(Command("remove"))
async def remove_handler(message: Message) -> None:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("Формат: /remove 7707083893")
        return
    async with SessionLocal() as session:
        async with session.begin():
            removed = await remove_inn(session, message.from_user.id, parts[1])
    await message.answer("ИНН удалён." if removed else "Такого ИНН нет в вашем списке.")


@dp.message(Command("list"))
async def list_handler(message: Message) -> None:
    async with SessionLocal() as session:
        values = await list_inns(session, message.from_user.id)
    await message.answer("Ваши ИНН:\n" + ("\n".join(values) if values else "Список пуст."))


@dp.message(Command("settings"))
async def settings_handler(message: Message) -> None:
    await message.answer(f"Расписание: ежедневно в 09:00 ({settings.default_timezone}).\n"
                         "Изменение часового пояса будет добавлено в следующей итерации.")


async def main() -> None:
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is required to start the Telegram bot service.")
    bot = Bot(settings.bot_token)
    # Serialize polling across overlapping Railway deployments. PostgreSQL releases
    # this session-level advisory lock automatically if a container is terminated.
    try:
        async with engine.connect() as lock_connection:
            await lock_connection.execute(text("SELECT pg_advisory_lock(9296287990)"))
            try:
                await dp.start_polling(bot)
            finally:
                await lock_connection.execute(text("SELECT pg_advisory_unlock(9296287990)"))
    finally:
        await bot.session.close()
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
