"""Type definitions for UltimaScraper.

This package contains:
- protocols: Protocol definitions for duck typing with type safety
- guards: Runtime type guards for type narrowing
"""

from ultima_scraper_core.typings.guards import (
    has_auth_id,
    has_auths,
    has_engine,
    has_find_auth,
    has_redis,
    has_redis_manager,
    has_subscriptions,
    has_ultima_scraper_api,
)
from ultima_scraper_core.typings.protocols import (
    HasAuth,
    HasAuths,
    HasEngine,
    HasFindAuth,
    HasRedis,
    HasRedisManager,
    HasSubscriptions,
    HasUltimaScraperAPI,
)

__all__ = [
    # Protocols
    "HasUltimaScraperAPI",
    "HasEngine",
    "HasRedis",
    "HasRedisManager",
    "HasAuth",
    "HasSubscriptions",
    "HasFindAuth",
    "HasAuths",
    # Type guards
    "has_ultima_scraper_api",
    "has_engine",
    "has_redis",
    "has_redis_manager",
    "has_auth_id",
    "has_subscriptions",
    "has_find_auth",
    "has_auths",
]
