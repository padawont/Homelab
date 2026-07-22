---
title: "Forgejo Registries"
status: draft
tags:
  - git
  - forge
  - registry
  - container
  - packages
sources:
  - url: "https://forgejo.org/docs/latest/user/packages/"
    title: "Forgejo Package Registry"
  - url: "https://forgejo.org/docs/latest/user/packages/container/"
    title: "Forgejo Container Registry"
  - url: "https://forgejo.org/docs/latest/user/packages/npm/"
    title: "Forgejo npm Registry"
  - url: "https://forgejo.org/docs/latest/user/packages/pypi/"
    title: "Forgejo PyPI Registry"
  - url: "https://forgejo.org/docs/latest/user/packages/maven/"
    title: "Forgejo Maven Registry"
  - url: "https://forgejo.org/docs/latest/user/packages/cargo/"
    title: "Forgejo Cargo Registry"
last_audit_date: 2026-07-22
related_configs:
  - "configs-and-adr/node-main/kubernetes/forgejo.yaml"
---

# Forgejo Registries

Forgejo includes a built-in package registry that supports multiple formats. Each repository can have its own package list, and packages are associated with the repository (or organization/user) that owns them.

## Container Registry (OCI)

Forgejo provides an OCI-compatible container registry at:

```
git.homelab.internal/<owner>/<repo>/-/packages/container/
```

### Authentication

```bash
docker login git.homelab.internal
```

Use a Forgejo personal access token (with package read/write scope) as the password.

### Push an Image

```bash
docker tag myimage:latest git.homelab.internal/owner/repo:latest
docker push git.homelab.internal/owner/repo:latest
```

### Pull an Image

```bash
docker pull git.homelab.internal/owner/repo:latest
```

## npm Registry

Configure `.npmrc`:

```
registry=https://git.homelab.internal/_packaging/<owner>/npm/
//git.homelab.internal/_packaging/<owner>/npm/:_authToken=<token>
```

Publish:

```bash
npm publish
```

## PyPI Registry

Configure `.pypirc`:

```
[distutils]
index-servers = forgejo

[forgejo]
repository = https://git.homelab.internal/_packaging/<owner>/pypi/
username = <username>
password = <token>
```

Publish:

```bash
python -m twine upload --repository forgejo dist/*
```

## Maven Registry

Configure `pom.xml`:

```xml
<distributionManagement>
  <repository>
    <id>forgejo</id>
    <url>https://git.homelab.internal/_packaging/<owner>/maven/</url>
  </repository>
</distributionManagement>
```

Configure `settings.xml` with authentication credentials.

## Cargo Registry

Configure `.cargo/config.toml`:

```toml
[registries]
forgejo = { index = "https://git.homelab.internal/_packaging/<owner>/cargo/" }
```

## Other Supported Formats

Forgejo's package registry supports 20+ formats including Alpine, Arch Linux, Chef, Composer, Conan, Conda, CRAN, Debian, Generic, Go, Helm, NuGet, Pub, RPM, RubyGems, Swift, and Vagrant.

## Package Management in the UI

- Package list per repository, organization, or user
- Package details page with install instructions
- Package deletion and version management
- Quota limits for storage usage
