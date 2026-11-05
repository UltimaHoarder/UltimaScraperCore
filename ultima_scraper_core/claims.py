"""First-visitor checks shared by the backend and the WebUI server.

An unconfigured service may let the first browser on its own network finish
setup without a credential. These helpers decide whether a request comes from
loopback or a private network.
"""

from __future__ import annotations

import ipaddress


def is_private_address(value: str) -> bool:
    """Loopback, private, link-local and other non-globally-routable addresses."""
    try:
        return ipaddress.ip_address(value.strip()).is_private
    except ValueError:
        return False


def visitor_is_local(peer: str | None, forwarded_for: str | None) -> bool:
    """Whether the browser behind a request is on loopback or a private network.

    ``peer`` is the address that connected. When it is itself private (a proxy
    such as the WebUI in front of the backend), the last ``X-Forwarded-For`` hop
    is the browser: that proxy appended it, so earlier hops a client could have
    forged are ignored. Behind another reverse proxy, that proxy is what is seen.
    """
    if not peer or not is_private_address(peer):
        return False
    if not forwarded_for:
        return True
    return is_private_address(forwarded_for.split(",")[-1])
