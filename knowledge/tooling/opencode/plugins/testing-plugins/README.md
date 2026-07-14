# Testing OpenCode Plugins

Strategies, patterns, and complete code examples for testing OpenCode plugins: init hook file-copy logic, event handler guards, mock setup for `@opencode-ai/plugin` types, and CI pipeline configuration.

## Files

- `overview.md` -- Comprehensive reference: mocking plugin context, testing file-copy operations, event handler unit tests, and GitHub Actions CI workflow

## Cross-References

- [`../creation.md`](../creation.md) -- Plugin structure and the factory function pattern that tests exercise
- [`../init-hook-lifecycle.md`](../init-hook-lifecycle.md) -- Init hook lifecycle: version-stamping, file-copy, self-healing (the code under test)
- [`../bundling-components.md`](../bundling-components.md) -- Component copy patterns (agents, skills, tools) that the init hook provisions
