# Ultima Scraper Core

`ultima-scraper-core` contains the small, stable contracts shared by
UltimaScraper services. It deliberately has no dependency on the backend,
database, control plane, plugin runtime, or scraper implementations.

## Intended contents

- Type guards and structural protocols
- Domain identifiers, enums, and value objects once they are used by multiple packages
- Job/task or event contracts once they are independent of a runtime implementation
- Common exceptions and lightweight utilities

## Dependency rule

`ultima_scraper_core` may be imported by the backend, database, archive, and API
packages. It must not import any of them. The control plane, plugin runtime,
storage implementations, and worker processes remain in their owning packages.

```text
ultima_scraper_core
        ^
        |
backend / database / archive / API
```

Framework-specific code—FastAPI routes, SQLAlchemy models, Redis clients,
worker processes, and concrete scraper integrations—belongs in the package
that implements it rather than here.

## Development

From this directory:

```bash
uv sync --group dev
uv run pytest
```
