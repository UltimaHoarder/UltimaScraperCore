"""Type guards for runtime type checking in UltimaScraper.

Type guards provide runtime type narrowing while maintaining type safety.
They replace hasattr checks with proper type-safe alternatives.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeGuard

if TYPE_CHECKING:
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


def has_ultima_scraper_api(obj: Any) -> TypeGuard[HasUltimaScraperAPI]:
    """Check if object has UltimaScraperAPI wrapper instance.

    This is the centralized wrapper that provides access to all site APIs
    via api_instances.OnlyFans, api_instances.Fansly, etc.

    Args:
        obj: Object to check

    Returns:
        True if object has 'ultima_scraper_api' attribute with UltimaScraperAPI type
    """
    return hasattr(obj, "ultima_scraper_api") and obj.ultima_scraper_api is not None


def has_engine(obj: Any) -> TypeGuard[HasEngine]:
    """Check if object has a database engine.

    Args:
        obj: Object to check

    Returns:
        True if object has 'engine' attribute
    """
    return hasattr(obj, "engine") and obj.engine is not None


def has_redis(obj: Any) -> TypeGuard[HasRedis]:
    """Check if object has a Redis connection.

    Args:
        obj: Object to check

    Returns:
        True if object has 'redis' attribute
    """
    return hasattr(obj, "redis") and obj.redis is not None


def has_redis_manager(obj: Any) -> TypeGuard[HasRedisManager]:
    """Check if object has a RedisManager with get_redis method.

    Args:
        obj: Object to check

    Returns:
        True if object has get_redis method
    """
    return hasattr(obj, "get_redis") and callable(obj.get_redis)


def has_auth_id(obj: Any) -> TypeGuard[HasAuth]:
    """Check if object has auth-like structure with id and username.

    Args:
        obj: Object to check

    Returns:
        True if object has 'id' attribute
    """
    return hasattr(obj, "id") and obj.id is not None


def has_subscriptions(obj: Any) -> TypeGuard[HasSubscriptions]:
    """Check if object has subscription management capabilities.

    Args:
        obj: Object to check

    Returns:
        True if object has 'subscriptions' attribute and get_user method
    """
    return (
        hasattr(obj, "subscriptions")
        and hasattr(obj, "get_user")
        and callable(obj.get_user)
    )


def has_find_auth(obj: Any) -> TypeGuard[HasFindAuth]:
    """Check if API instance can find auth by ID.

    Args:
        obj: Object to check

    Returns:
        True if object has 'find_auth' method
    """
    return hasattr(obj, "find_auth") and callable(obj.find_auth)


def has_auths(obj: Any) -> TypeGuard[HasAuths]:
    """Check if API instance has multiple auths.

    Args:
        obj: Object to check

    Returns:
        True if object has 'auths' attribute (list or dict)
    """
    return hasattr(obj, "auths") and isinstance(obj.auths, (list, dict))
