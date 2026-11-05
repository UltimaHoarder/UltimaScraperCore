"""Shared environment-file helpers for UltimaScraper services."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Mapping

from platformdirs import user_config_dir

from .files import atomic_write_text, file_lock


def get_env_path() -> Path:
    """Return the active UltimaScraper ``.env`` path.

    Resolution order:
    1. Explicit override via ULTIMA_ENV_PATH if set.
    2. Component user config: ~/.config/ultima_scraper_verse/UltimaScraper/.env
    """
    explicit = os.environ.get("ULTIMA_ENV_PATH")
    if explicit:
        return Path(explicit)

    return (
        Path(user_config_dir("ultima_scraper_verse")) / "UltimaScraper" / ".env"
    )


def find_local_env_path() -> Path | None:
    """Find a local workspace or repository-root .env file, if present."""
    repo_root = os.environ.get("USR_REPOSITORY_ROOT")
    if repo_root:
        try:
            repo_candidate = Path(repo_root) / ".env"
            if repo_candidate.is_file():
                return repo_candidate
        except OSError:
            pass

    try:
        cwd_candidate = Path.cwd() / ".env"
        if cwd_candidate.is_file():
            return cwd_candidate
    except OSError:
        pass

    return None


def read_env(path: Path | str | None = None) -> dict[str, str]:
    """Read a dotenv-style file without mutating the process environment."""
    env_path = Path(path) if path is not None else get_env_path()
    try:
        lines = env_path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return {}
    except OSError as exc:
        raise RuntimeError(
            f"Unable to read environment file {env_path}: {exc}"
        ) from exc

    values: dict[str, str] = {}
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            if value[0] == '"':
                try:
                    value = json.loads(value)
                except ValueError:
                    value = value[1:-1]
            else:
                value = value[1:-1]
        if key:
            values[key] = value
    return values


def write_env(values: Mapping[str, object], path: Path | str | None = None) -> None:
    """Explicitly replace an environment file; use ``update_env`` for shared edits."""
    env_path = Path(path) if path is not None else get_env_path()
    env_path.parent.mkdir(parents=True, exist_ok=True)
    contents = "".join(_env_line(key, value) for key, value in values.items())
    with file_lock(env_path):
        atomic_write_text(env_path, contents)


def _env_line(key: str, value: object) -> str:
    if re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", key) is None:
        raise ValueError("Invalid environment variable name")
    text = str(value)
    if any(character in text for character in ("\n", "\r", "\0")):
        raise ValueError(f"{key} must be a single-line value")
    return f"{key}={json.dumps(text, ensure_ascii=False)}\n"


def update_env(
    values: Mapping[str, object | None],
    path: Path | str | None = None,
    *,
    overwrite: bool = True,
) -> None:
    """Atomically update owned keys, preserving unrelated lines; ``None`` deletes."""
    env_path = Path(path) if path is not None else get_env_path()
    env_path.parent.mkdir(parents=True, exist_ok=True)
    replacement = {
        key: _env_line(key, value) if value is not None else None
        for key, value in values.items()
    }
    for key in values:
        _env_line(key, "")
    with file_lock(env_path):
        try:
            lines = env_path.read_text(encoding="utf-8").splitlines(keepends=True)
        except FileNotFoundError:
            lines = []
        if not overwrite:
            existing = read_env(env_path)
            replacement = {
                key: value for key, value in replacement.items() if key not in existing
            }
        pending = dict(replacement)
        output: list[str] = []
        for line in lines:
            match = re.match(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z_0-9]*)\s*=", line)
            key = match.group(1) if match else None
            if key not in replacement:
                output.append(line)
            elif key in pending:
                value = pending.pop(key)
                if value is not None:
                    output.append(value)
        if output and not output[-1].endswith("\n"):
            output[-1] += "\n"
        output.extend(value for value in pending.values() if value is not None)
        atomic_write_text(env_path, "".join(output))


def load_env(
    path: Path | str | None = None, *, overwrite: bool = False
) -> dict[str, str]:
    """Load values into ``os.environ`` with layered precedence and return the parsed mapping.

    Resolution precedence (highest to lowest):
    1. Pre-existing ``os.environ`` variables (e.g. from container or shell)
    2. Local workspace ``.env`` file (if present in cwd or repo root)
    3. User configuration file (~/.config/ultima_scraper_verse/UltimaScraper/.env)
    """
    if path is not None:
        values = read_env(path)
        for key, value in values.items():
            if overwrite:
                os.environ[key] = value
            else:
                os.environ.setdefault(key, value)
        return values

    config_path = get_env_path()
    values = read_env(config_path)

    local_path = find_local_env_path()
    if local_path is not None:
        try:
            is_same = local_path.resolve() == config_path.resolve()
        except OSError:
            is_same = local_path == config_path

        if not is_same:
            local_values = read_env(local_path)
            values.update(local_values)

    for key, value in values.items():
        if overwrite:
            os.environ[key] = value
        else:
            os.environ.setdefault(key, value)
    return values


def runtime_env_value(name: str, path: Path | str | None = None) -> str | None:
    """Resolve a setting from the process first, then local or shared env files."""
    value = os.environ.get(name)
    if value is not None:
        return value
    if path is not None:
        return read_env(path).get(name)
    local_path = find_local_env_path()
    if local_path is not None:
        local_val = read_env(local_path).get(name)
        if local_val is not None:
            return local_val
    return read_env(get_env_path()).get(name)


def archive_database_url(site: str | None = None) -> str | None:
    """Canonical archive URL, with explicit legacy aliases at each source tier."""
    names = ["ULTIMA_ARCHIVE_DATABASE_URL", "DATABASE_URL"]
    if site:
        names.insert(0, f"{site.upper()}_DATABASE_URL")
    for name in names:
        if name in os.environ:
            return os.environ[name]
    local_path = find_local_env_path()
    if local_path is not None:
        local_values = read_env(local_path)
        match = next(
            (local_values[name] for name in names if name in local_values), None
        )
        if match is not None:
            return match
    values = read_env(get_env_path())
    return next((values[name] for name in names if name in values), None)
