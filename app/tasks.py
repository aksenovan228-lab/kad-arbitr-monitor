import asyncio
import logging
from sqlalchemy import select

from app.celery_app import celery_app
from app.db import SessionLocal
from app.models import TrackedInn
from app.kad_client import build_kad_client, ProviderNotConfigured

log = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.dispatch_checks")
def dispatch_checks() -> dict[str, int]:
    return asyncio.run(_dispatch_checks())


async def _dispatch_checks() -> dict[str, int]:
    async with SessionLocal() as session:
        inns = list((await session.scalars(select(TrackedInn.inn).distinct())).all())

    client = build_kad_client()
    skipped = 0
    try:
        for inn in inns:
            try:
                await client.search_by_inn(inn)
            except ProviderNotConfigured:
                skipped += 1
                log.warning("KAD provider disabled; no query executed")
                break
    finally:
        await client.close()
    return {"tracked_inns_seen": len(inns), "skipped_provider_disabled": skipped}
