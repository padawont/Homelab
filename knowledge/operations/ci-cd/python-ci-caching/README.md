# CI Caching for Python

CI caching strategies for Python projects in GitHub Actions — uv dependency caching, VCR cassette caching, and Docker layer caching.

## Contents

- [overview.md](./overview.md) — Topic hub and index

### Cache Action & Key Design
- [cache-action-overview.md](./cache-action-overview.md) — actions/cache basics
- [cache-key-strategies.md](./cache-key-strategies.md) — Key design principles
- [cache-key-lockfile-hash.md](./cache-key-lockfile-hash.md) — hashFiles('**/lockfile') key
- [cache-key-os-factor.md](./cache-key-os-factor.md) — OS in cache key
- [cache-key-python-version.md](./cache-key-python-version.md) — Python version in cache key
- [cache-restore-keys.md](./cache-restore-keys.md) — restore-keys fallback patterns

### Cache Paths
- [cache-path-pip.md](./cache-path-pip.md) — ~/.cache/pip path
- [cache-path-uv.md](./cache-path-uv.md) — UV cache directory (~/.cache/uv)
- [cache-path-venv.md](./cache-path-venv.md) — .venv directory cache

### Cache Hit Detection
- [cache-hit-detection.md](./cache-hit-detection.md) — Cache hit/miss logic in steps

### Dependency Caching — pip (legacy)
- [pip-caching-setup.md](./pip-caching-setup.md) — actions/setup-python cache: pip

### Dependency Caching — uv
- [uv-caching-install.md](./uv-caching-install.md) — astral-sh/setup-uv action caching
- [uv-cache-dependency-glob.md](./uv-cache-dependency-glob.md) — uv cache key with cache-dependency-glob
- [uv-cache-segmented.md](./uv-cache-segmented.md) — UV cache segments
- [pip-vs-uv-tradeoffs.md](./pip-vs-uv-tradeoffs.md) — Speed, reliability, disk usage comparison

### VCR Cassette Caching
- [vcr-cassette-caching-intro.md](./vcr-cassette-caching-intro.md) — Why cache cassettes in CI
- [vcr-cache-key.md](./vcr-cache-key.md) — Cassette cache key design
- [vcr-cache-path.md](./vcr-cache-path.md) — Cassette directory cache path
- [vcr-cache-invalidation.md](./vcr-cache-invalidation.md) — When keys should bust cache
- [vcr-cache-selective-recording.md](./vcr-cache-selective-recording.md) — Only re-record changed endpoints
- [vcr-cache-miss-handling.md](./vcr-cache-miss-handling.md) — What happens on cache miss

### Prek (pre-commit hooks)
- [prek-caching-overview.md](./prek-caching-overview.md) — Prek hook environments
- [prek-cache-key.md](./prek-cache-key.md) — Prek cache key strategies
- [prek-cache-restore.md](./prek-cache-restore.md) — Prek restore patterns

### Docker Layer Caching
- [docker-layer-caching-intro.md](./docker-layer-caching-intro.md) — Docker layer caching (DLC)
- [docker-dlc-key.md](./docker-dlc-key.md) — DLC cache key design
- [docker-dlc-invalidation.md](./docker-dlc-invalidation.md) — When to bust DLC
- [docker-multi-stage.md](./docker-multi-stage.md) — Multi-stage build for cache

### Benchmarks
- [benchmark-pip-timing.md](./benchmark-pip-timing.md) — Pip install benchmark data
- [benchmark-uv-timing.md](./benchmark-uv-timing.md) — UV install benchmark data
- [benchmark-vcr-speedup.md](./benchmark-vcr-speedup.md) — Cassette replay vs live speedup

### Troubleshooting
- [troubleshooting.md](./troubleshooting.md) — Common caching issues
