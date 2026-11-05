"""Self-signed certificates and their fingerprints, shared by the WebUI and backends.

``cryptography`` is imported where it is used, so this package stays
dependency-light; whatever serves HTTPS depends on it.
"""

from __future__ import annotations

import datetime as dt
import ipaddress
import socket
from dataclasses import dataclass
from pathlib import Path

_VALID_FOR = dt.timedelta(days=825)
# Renewed this long before it expires.
_RENEW_BEFORE = dt.timedelta(days=30)


@dataclass(frozen=True)
class TLSFiles:
    cert_file: Path
    key_file: Path
    self_signed: bool = False


def _names(extra: list[str]) -> list[str]:
    names = ["localhost", "127.0.0.1", "::1", socket.gethostname()]
    try:
        names.append(socket.getfqdn())
        # This machine's LAN address, as other devices on the network reach it.
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
            probe.connect(("192.0.2.1", 9))
            names.append(probe.getsockname()[0])
    except OSError:
        pass
    seen: list[str] = []
    for name in [*names, *extra]:
        if name and name not in seen:
            seen.append(name)
    return seen


def _subject_alternative_names(names: list[str]):
    from cryptography import x509

    entries = []
    for name in names:
        try:
            entries.append(x509.IPAddress(ipaddress.ip_address(name)))
        except ValueError:
            entries.append(x509.DNSName(name))
    return x509.SubjectAlternativeName(entries)


def _current(cert_file: Path, names: list[str]) -> bool:
    """The kept certificate still covers these names and is not near expiry."""
    from cryptography import x509

    try:
        certificate = x509.load_pem_x509_certificate(cert_file.read_bytes())
    except (OSError, ValueError):
        return False
    if certificate.not_valid_after_utc - dt.datetime.now(dt.UTC) < _RENEW_BEFORE:
        return False
    try:
        present = certificate.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
    except x509.ExtensionNotFound:
        return False
    wanted = _subject_alternative_names(names)
    return all(entry in present for entry in wanted)


def ensure_self_signed(
    directory: Path, extra_names: list[str] | None = None, *, common_name: str = "UltimaScraper"
) -> TLSFiles:
    """Create (or renew) the self-signed certificate; reuse it while it is current."""
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    cert_file, key_file = directory / "cert.pem", directory / "key.pem"
    names = _names(extra_names or [])
    if key_file.is_file() and _current(cert_file, names):
        return TLSFiles(cert_file, key_file, self_signed=True)

    key = ec.generate_private_key(ec.SECP256R1())
    now = dt.datetime.now(dt.UTC)
    subject = x509.Name(
        [x509.NameAttribute(NameOID.COMMON_NAME, f"{common_name} ({socket.gethostname()})")]
    )
    certificate = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - dt.timedelta(minutes=5))
        .not_valid_after(now + _VALID_FOR)
        .add_extension(_subject_alternative_names(names), critical=False)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
        .sign(key, hashes.SHA256())
    )
    temporary_key = key_file.with_suffix(".tmp")
    temporary_key.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
        )
    )
    temporary_key.chmod(0o600)
    temporary_key.replace(key_file)
    cert_file.write_bytes(certificate.public_bytes(serialization.Encoding.PEM))
    return TLSFiles(cert_file, key_file, self_signed=True)


def fingerprint(cert_file: Path) -> str:
    """SHA-256 fingerprint, as browsers show it, to check before trusting."""
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes

    digest = x509.load_pem_x509_certificate(cert_file.read_bytes()).fingerprint(hashes.SHA256())
    return ":".join(f"{byte:02X}" for byte in digest)


def fingerprint_der(der: bytes) -> str:
    """The same fingerprint, for a certificate as a peer presents it (DER bytes)."""
    import hashlib

    return ":".join(f"{byte:02X}" for byte in hashlib.sha256(der).digest())
