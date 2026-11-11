from dataclasses import dataclass
from typing import Protocol


class ProviderNotConfigured(RuntimeError):
    pass


@dataclass(frozen=True)
class CaseHit:
    case_number: str
    court: str
    registered_at: str
    url: str
    participant_role: str


class KadClient(Protocol):
    async def search_by_inn(self, inn: str) -> list[CaseHit]: ...
    async def close(self) -> None: ...


class DisabledKadClient:
    """Safe default: no undocumented endpoints, browser automation or CAPTCHA bypass."""

    async def search_by_inn(self, inn: str) -> list[CaseHit]:
        raise ProviderNotConfigured(
            "KAD provider is disabled. Configure a permitted documented or licensed provider."
        )

    async def close(self) -> None:
        return None


def build_kad_client() -> KadClient:
    # Intentionally fail closed until an approved provider adapter is implemented.
    return DisabledKadClient()
