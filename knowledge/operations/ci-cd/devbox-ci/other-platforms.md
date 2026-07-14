---
title: "Devbox CI/CD — Other Platforms"
status: draft
author: "Khalid"
date: 2026-05-24
tags: ["devbox", "gitlab-ci", "circleci", "ci-cd"]
sources:
  - url: "https://www.jetify.com/docs/devbox/installing-devbox/"
    title: "Devbox — Installing Devbox"
last_audit_date: 2026-05-24
---

# Devbox CI/CD — Other Platforms

Devbox works on any Linux runner. For GitLab CI, CircleCI, etc., install Devbox manually and use the standard CLI:

```yaml
# GitLab CI example
variables:
  DEVBOX_USE_VERSION: "0.13.4"

before_script:
  - curl -fsSL https://get.jetify.com/devbox | bash
  - devbox install

test:
  script:
    - devbox run test
```

For caching on non-GitHub platforms, use a Cachix binary cache or your CI provider's cache mechanism to persist `/nix/store`.
