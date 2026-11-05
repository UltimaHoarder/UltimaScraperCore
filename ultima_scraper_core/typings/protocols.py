"""Protocol definitions for common interfaces in UltimaScraper.

These protocols allow for duck typing with proper type safety,
replacing hasattr/getattr patterns with static type checking.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from redis.asyncio import Redis
    from sqlalchemy.engine import Engine
    from ultima_scraper_api import UltimaScraperAPI, auth_types


@runtime_checkable
class HasUltimaScraperAPI(Protocol):
    """Protocol for objects that have the centralized UltimaScraperAPI wrapper.

    Common in Worker: self.ultima_scraper_api = UltimaScraperAPI()
    Provides access to all site APIs via api_instances.OnlyFans, api_instances.Fansly, etc.
    """

    ultima_scraper_api: UltimaScraperAPI


@runtime_checkable
class HasEngine(Protocol):
    """Protocol for objects that have a database engine."""

    engine: Engine


@runtime_checkable
class HasRedis(Protocol):
    """Protocol for objects that have a Redis connection."""

    redis: Redis[Any]


@runtime_checkable
class HasRedisManager(Protocol):
    """Protocol for objects that have a RedisManager with get_redis method."""

    def get_redis(self) -> Redis[Any]:
        """Get Redis connection."""
        ...


@runtime_checkable
class HasAuth(Protocol):
    """Protocol for API objects that have authentication."""

    @property
    def id(self) -> int:
        """Auth account ID."""
        ...

    @property
    def username(self) -> str | None:
        """Auth account username."""
        ...


@runtime_checkable
class HasSubscriptions(Protocol):
    """Protocol for auth objects with subscription management."""

    subscriptions: list[Any] | dict[int | str, Any]

    async def get_user(self, identifier: int | str) -> Any:
        """Fetch user by ID or username."""
        ...


@runtime_checkable
class HasFindAuth(Protocol):
    """Protocol for API instances that can find auth by ID."""

    def find_auth(self, account_id: int) -> auth_types | None:
        """Find authentication instance by account ID."""
        ...


@runtime_checkable
class HasAuths(Protocol):
    """Protocol for API instances with multiple auths."""

    auths: list[auth_types] | dict[int | str, auth_types]
