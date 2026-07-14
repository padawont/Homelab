# pytest & Async Testing

Python testing patterns focused on async testing with FastAPI, VCR.py, and LLM evaluation.

## Getting Started

- [installation.md](./installation.md) — uv add pytest + plugins
- [test-discovery.md](./test-discovery.md) — Naming conventions and collection rules
- [assertions.md](./assertions.md) — assert, raises, approx
- [troubleshooting.md](./troubleshooting.md) — Common issues and fixes

## pytest Basics

- [fixtures-intro.md](./fixtures-intro.md) — @pytest.fixture basics
- [fixtures-scope.md](./fixtures-scope.md) — function, class, module, session scopes
- [fixtures-autouse.md](./fixtures-autouse.md) — autouse=True patterns
- [fixtures-parametrize-fixtures.md](./fixtures-parametrize-fixtures.md) — @pytest.fixture(params=...)
- [fixtures-conftest.md](./fixtures-conftest.md) — Shared fixtures via conftest.py
- [fixtures-tmpdir.md](./fixtures-tmpdir.md) — tmp_path, tmpdir fixtures
- [fixtures-monkeypatch.md](./fixtures-monkeypatch.md) — monkeypatch.setattr, setenv
- [fixtures-request.md](./fixtures-request.md) — Request object for fixture introspection

## Parametrization

- [parametrize-intro.md](./parametrize-intro.md) — @pytest.mark.parametrize
- [parametrize-multiple.md](./parametrize-multiple.md) — Multiple argument sets
- [parametrize-cartesian.md](./parametrize-cartesian.md) — Cross-product parametrization
- [parametrize-fixture-combine.md](./parametrize-fixture-combine.md) — Combining fixtures with parametrize

## Marks

- [marks-builtin.md](./marks-builtin.md) — skip, skipif, xfail, parametrize
- [marks-custom.md](./marks-custom.md) — Custom markers and registration
- [markers-conditional-skip.md](./markers-conditional-skip.md) — Conditional skip patterns

## Plugin System

- [plugin-system-overview.md](./plugin-system-overview.md) — Architectural overview of pluggy, plugin types, lifecycle
- [plugin-registration.md](./plugin-registration.md) — All discovery mechanisms: conftest, entry points, env var, -p flag
- [plugin-hooks-reference.md](./plugin-hooks-reference.md) — Complete reference of hooks by lifecycle phase
- [writing-plugins.md](./writing-plugins.md) — Authoring and packaging plugins for distribution
- [testing-plugins.md](./testing-plugins.md) — Testing plugins with pytester

## Conftest & Configuration

- [conftest-intro.md](./conftest-intro.md) — What conftest.py does
- [conftest-hooks.md](./conftest-hooks.md) — pytest_runtest_setup, etc.
- [config-pyproject-toml.md](./config-pyproject-toml.md) — [tool.pytest.ini_options]
- [config-pytest-ini.md](./config-pytest-ini.md) — pytest.ini settings
- [config-addopts.md](./config-addopts.md) — Default CLI options
- [config-testpaths.md](./config-testpaths.md) — Test root directories
- [config-markers.md](./config-markers.md) — Marker registration

## pytest-asyncio

- [pytest-asyncio-installation.md](./pytest-asyncio-installation.md) — uv add, conftest setup
- [pytest-asyncio-marks.md](./pytest-asyncio-marks.md) — @pytest.mark.asyncio
- [pytest-asyncio-fixtures.md](./pytest-asyncio-fixtures.md) — Async fixtures
- [pytest-asyncio-scope.md](./pytest-asyncio-scope.md) — Async fixture scoping
- [pytest-asyncio-event-loop.md](./pytest-asyncio-event-loop.md) — Custom event loop fixture

## Coverage (pytest-cov)

- [pytest-cov-installation.md](./pytest-cov-installation.md) — uv add pytest-cov
- [pytest-cov-basic-usage.md](./pytest-cov-basic-usage.md) — --cov, --cov-report
- [pytest-cov-config-file.md](./pytest-cov-config-file.md) — [tool.coverage.run]
- [pytest-cov-thresholds.md](./pytest-cov-thresholds.md) — fail_under, --cov-fail-under
- [pytest-cov-omit.md](./pytest-cov-omit.md) — Omitting files from coverage

## FastAPI Testing

- [fastapi-testclient-intro.md](./fastapi-testclient-intro.md) — TestClient from starlette.testclient
- [fastapi-testclient-context.md](./fastapi-testclient-context.md) — with TestClient(app) as client
- [fastapi-testclient-headers.md](./fastapi-testclient-headers.md) — Setting headers
- [fastapi-testclient-cookies.md](./fastapi-testclient-cookies.md) — Cookie handling
- [fastapi-testclient-json.md](./fastapi-testclient-json.md) — JSON send/receive
- [fastapi-testclient-auth.md](./fastapi-testclient-auth.md) — Auth header patterns
- [fastapi-dependency-override-single.md](./fastapi-dependency-override-single.md) — Overriding dependencies
- [fastapi-dependency-override-clear.md](./fastapi-dependency-override-clear.md) — Clearing overrides

## Async HTTP Testing (httpx)

- [httpx-async-client-intro.md](./httpx-async-client-intro.md) — AsyncClient from httpx
- [httpx-async-client-fastapi.md](./httpx-async-client-fastapi.md) — AsyncClient with ASGITransport
- [httpx-async-client-streaming.md](./httpx-async-client-streaming.md) — SSE/streaming endpoints
- [httpx-async-client-websockets.md](./httpx-async-client-websockets.md) — WebSocket testing

## Async Fixture Patterns

- [async-fixtures-database.md](./async-fixtures-database.md) — DB setup/teardown
- [async-fixtures-api-client.md](./async-fixtures-api-client.md) — Client session fixture
- [async-fixtures-temporary-data.md](./async-fixtures-temporary-data.md) — Test data creation

## pytest-vcr / Cassette Recording

- [pytest-vcr-fixtures.md](./pytest-vcr-fixtures.md) — vcr_config fixture
- [pytest-vcr-cassette-dir.md](./pytest-vcr-cassette-dir.md) — Cassette directory configuration
- [pytest-vcr-matchers-filtering.md](./pytest-vcr-matchers-filtering.md) — Matchers and filters
- [pytest-vcr-recording-patterns.md](./pytest-vcr-recording-patterns.md) — Recording strategies

## CI/CD

- [ci-github-actions-run.md](./ci-github-actions-run.md) — pytest in GitHub Actions with uv
- [ci-matrix-testing.md](./ci-matrix-testing.md) — Python version matrix
- [ci-coverage-reporting.md](./ci-coverage-reporting.md) — Upload coverage to Codecov
