---
title: "RuneSmith Security Supply-Chain"
status: exploring
author: "refactorartist (Khalid Zubair)"
date: 2026-06-09
tags:
  - opencode
  - runesmith
  - security
  - supply-chain
  - npm
sources:
  - knowledge: "knowledge/tooling/opencode/plugins/github-packages-org-setup/overview.md"
  - knowledge: "knowledge/tooling/opencode/plugins/npm-packaging.md"
  - knowledge: "knowledge/tooling/opencode/plugins/bundling-components.md"
  - knowledge: "knowledge/tooling/opencode/plugins/publishing-workflow.md"
  - knowledge: "knowledge/tooling/opencode/skills/dependency-checker.md"
  - knowledge: "knowledge/tooling/opencode/agents/composition-patterns.md"
references:
  - url: "https://docs.npmjs.com/cli/v11/commands/npm-audit"
    title: "npm audit documentation"
  - url: "https://docs.github.com/en/packages/learn-github-packages/about-github-packages"
    title: "About GitHub Packages"
  - url: "https://docs.github.com/en/packages/learn-github-packages/about-permissions-for-github-packages"
    title: "GitHub Packages permissions and security"
  - url: "https://cyclonedx.org/"
    title: "CycloneDX SBOM standard"
  - url: "https://docs.npmjs.com/generating-provenance-statements"
    title: "npm provenance statements"
last_audit_date: 2026-06-09
---

# RuneSmith Security Supply-Chain

The `@runicengines/opencode-runesmith` plugin is an internal npm package published to GitHub Packages. While the plugin itself is small and its dependency tree shallow, it participates in a supply chain that spans the npm registry ecosystem, the GitHub Packages trust boundary, and every developer workstation in the RunicEngines cooperative. This document analyses the security posture of that supply chain and provides actionable recommendations.

Related research in this series:

- [distribution-comparison.md](distribution-comparison.md) — how the plugin is packaged and distributed
- [init-hook.md](init-hook.md) — init hook lifecycle and file copying into consumer projects
- [package-structure.md](package-structure.md) — package layout and dependency declarations
- [permission-profiles.md](../operations/permission-profiles.md) — agent permission boundaries

---

## npm Dependency Risks

### Dependency Tree Overview

The plugin's direct dependency surface is intentionally narrow:

| Dependency Type | Primary Package | Rationale |
|---|---|---|
| `dependencies` | `@opencode-ai/plugin` | OpenCode plugin SDK — required at runtime |
| `devDependencies` | TypeScript, `@types/*`, build tools | Compilation and type checking — not shipped |
| `peerDependencies` | None currently | No shared runtime requirements with consumers |
| `bundledDependencies` | None currently | All agents and skills are static `.md` files copied by init hook |

The narrow production dependency tree is a strong security posture by default. Only one runtime dependency (`@opencode-ai/plugin`) enters the consumer's OpenCode process. However, even a single transitive dependency creates a vector for supply chain compromise.

### Supply Chain Attack Vectors

A compromised upstream package can affect RuneSmith in several ways:

1. **Direct dependency takeover** — The `@opencode-ai/plugin` package maintainer account is compromised and a malicious version is published.
2. **Transitive dependency hijack** — A dependency of `@opencode-ai/plugin` (or its dependencies) is hijacked via typo-squatting, account takeover, or malicious maintainer insertion.
3. **DevDependency escalation** — Compromised build tools during the plugin's CI pipeline inject malicious code into the published artifact. Because the plugin is not build-signed and has no integrity verification beyond npm's built-in checksums, this is detectable only through audit tooling.
4. **Dependency confusion** — A public package with the same name as an internal scoped package is published to the public npm registry. For the plugin itself this is mitigated by the `@runicengines` scope, which npm reserves for the organisation. For transitive dependencies, the `.npmrc` configuration determines which registry is consulted.

### npm Registry Security Model

The public npm registry provides several security mechanisms relevant to the plugin:

| Mechanism | What It Does | Applicable to RuneSmith |
|---|---|---|
| **Package integrity** | `integrity` field in lockfile (`sha512` hash) — verified on install | Yes — lockfile committed |
| **npm audit** | Scans resolved dependency tree against known vulnerability advisories | Yes — run in CI |
| **Provenance attestation** | OIDC-based build provenance linking package to source repo and CI run | No — GitHub Packages does not support npm provenance |
| **2FA requirement** | npm requires 2FA for publishing (or a granular access token with bypass 2FA enabled) | Yes — plugin maintainers should enable 2FA on npm accounts |
| **Dependabot alerts** | GitHub-native advisory scanning for published manifests | Yes — when plugin source is in a GitHub repo |

### Mitigation Strategies

| Mitigation | Recommendation | Priority |
|---|---|---|
| Lockfile | Commit `package-lock.json` to pin all transitive versions | High |
| Integrity hashes | Enabled by default with lockfile; verify during install | High |
| `npm audit` | Run in CI for every PR and release | High |
| Dependency reviews | Review `npm audit` output manually before release | Medium |
| Lockfile diff review | Review lockfile changes in PRs for unexpected additions | Medium |
| Provenance | Not available via GitHub Packages; accept this limitation | Low |

---

## GitHub Packages Trust Model

### How GitHub Packages Secures Packages

GitHub Packages authenticates package consumers through the same identity layer as the rest of GitHub. For npm packages, this means:

- **Authentication**: `GITHUB_TOKEN` or a personal access token (classic) with `read:packages` scope for consumers, `write:packages` for publishers.
- **Scope isolation**: The `@runicengines` scope is reserved for the GitHub organisation. No external party can publish to it. This prevents dependency confusion against the plugin name.
- **Access control**: By default, package visibility is tied to repository visibility. For the npm registry, granular permissions allow overriding this. For a private repository, the package is private by default and accessible only to users with access to the repository.
- **Audit trail**: All package downloads and publishes are logged in the GitHub audit log for the organisation.

### Comparison with Public npm Registry

| Aspect | Public npm Registry | GitHub Packages (npm) |
|---|---|---|
| **Authentication** | npm token (optional for public packages) | GITHUB_TOKEN / PAT required |
| **Default visibility** | Public | Private (tied to repo) |
| **Scope isolation** | Org scope reserved | Org scope reserved |
| **Provenance** | Supported (npm provenance) | Not supported |
| **2FA enforcement** | Available for packages | GitHub org-level 2FA |
| **Audit log** | npm audit log | GitHub audit log |
| **Dependency graph** | npm dependencies tab | GitHub Dependency Graph |
| **Package deletion** | Restricted (24h window for some) | Tied to repo deletion policy |

### Benefits for an Internal Plugin

- **Private by default**: No risk of accidental public exposure. Publishing requires explicit `--access public` plus registry permissions.
- **Org-scoped**: The `@runicengines` namespace is locked to the organisation. No external package can claim the name.
- **Unified authentication**: Developers already have GitHub credentials. No separate npm account management is needed.
- **Audit trail**: The GitHub audit log records who published which version and when. This satisfies basic compliance needs for a small cooperative.

### Limitations

- **No npm provenance attestation**: GitHub Packages does not support npm's OIDC-based provenance feature. There is no cryptographically verifiable link between the published package and the source repository commit that built it. For a small internal plugin this is acceptable, but it means supply chain integrity relies entirely on organisational trust and CI pipeline security rather than cryptographic attestation.
- **GitHub infrastructure dependency**: All consumers must have GitHub network access. Air-gapped or offline development setups cannot install or update the plugin.
- **Token management**: Each developer machine must be configured with appropriate `.npmrc` and `GITHUB_TOKEN` or PAT. Token expiry and rotation must be managed.

---

## Dependency Pinning vs Range Strategy

### Production Dependencies

**Recommendation: Pin exact versions.**

The sole production dependency `@opencode-ai/plugin` should be pinned to an exact version (e.g., `"@opencode-ai/plugin": "1.2.3"`) rather than using a semver range (`^1.2.3` or `~1.2.3`).

Rationale:

- The plugin is a binary-distributed tool, not a library. There is no benefit to semver flexibility for consumers — they do not install the plugin as a library dependency.
- An unexpected minor or patch release of `@opencode-ai/plugin` could introduce behavioral changes that break the plugin's init hook or event handlers.
- Pinning makes the dependency tree deterministic. Every install of the same plugin version pulls the exact same transitive dependency graph.
- Version bumps become intentional acts, reviewed in PRs, rather than silent changes on `npm install`.

The lockfile (`package-lock.json`) already pins transitive dependencies. Pinning the direct dependency in `package.json` adds a second layer of explicitness.

### Development Dependencies

**Recommendation: Semver ranges acceptable.**

DevDependencies (TypeScript, `@types/node`, `tsup`, etc.) are never shipped to consumers. They affect only the build environment. Using ranges reduces Dependabot noise and allows patch-level fixes to flow through automatically.

Recommended approach:

```json
{
  "devDependencies": {
    "@types/node": "^22.0.0",
    "tsup": "^8.0.0",
    "typescript": "^5.5.0"
  }
}
```

### Lockfile Strategy

**Recommendation: Commit `package-lock.json`.**

The lockfile must be committed to the plugin repository for two reasons:

1. **Deterministic installs**: Every CI run and every developer checkout produces the same transitive dependency graph.
2. **Diff-based audit**: Lockfile changes in PRs provide a visible record of dependency changes. Unexpected additions or version jumps are caught in code review.

Add `package-lock.json` to the repository if it is currently gitignored. Do not use `npm install --no-package-lock` in CI.

### Automated Dependency Updates

**Recommendation: Use Dependabot.**

Dependabot is the natural choice for a GitHub-hosted repository. Configuration in `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    versioning-strategy: increase
    labels:
      - "dependencies"
      - "security"
```

Key settings:

- `versioning-strategy: increase` — updates the version in `package.json` to the new resolved version (pinning). This is the correct choice for production dependencies. For devDependencies with ranges, `auto` may be preferred.
- Weekly schedule is appropriate for a low-velocity internal plugin. Security-critical patches can be expedited manually.
- The `dependencies` and `security` labels allow filtering PRs by dependency type.

### OpenCode Plugin Version Constraint

A notable limitation applies to how OpenCode resolves plugins. The `opencode.json` plugin array accepts package names without version specifiers:

```json
{
  "plugin": ["@runicengines/opencode-runesmith"]
}
```

Version resolution happens at the npm level (the installed package version in the Bun cache), not in the config file. This means:

- The plugin's own `package.json` version is the source of truth for consumers.
- Consumers cannot pin a specific version in `opencode.json`.
- Version management is delegated to the consumer's npm/Bun cache management practices.
- For the RunicEngines cooperative, this is acceptable — all developers install from the same GitHub Packages registry and can coordinate upgrades.

---

## Vulnerability Scanning

### Plugin's Own Dependencies

The plugin repository must scan its own dependency tree. This is distinct from the consumer-side scanning that the [dependency-checker skill](../../../knowledge/tooling/opencode/skills/dependency-checker.md) provides.

**Recommended scanning regimen:**

| Scan Type | Tool | Frequency |
|---|---|---|
| PR scan | `npm audit` | Every PR (CI gate) |
| Full scan | `npm audit --audit-level=high` | Every PR (CI gate), breaking on high/critical |
| Scheduled deep scan | Dependabot alerts | Continuous (GitHub-native) |
| Manual review | Developer review of Dependabot PRs | On each alert |

CI script for PR scanning:

```yaml
# .github/workflows/ci.yml (extract)
- name: Install dependencies
  run: npm ci
- name: Audit dependencies
  run: npm audit --audit-level=high
```

The `npm ci` command uses the lockfile for deterministic installs, which is the correct choice for CI. The `--audit-level=high` flag causes the build to fail on high or critical vulnerabilities.

### Dependabot Alerts

Enable Dependabot alerts in the plugin repository settings (Settings > Security & analysis > Dependabot alerts). This provides:

- Automatic detection of vulnerable dependencies in the default branch.
- PRs with version bumps to the minimum non-vulnerable version.
- GitHub-native notification via the Security tab and email.

### Consumer-Side Scanning

The RuneSmith plugin includes a `dependency-checker` skill that scans consumer projects. This skill is documented in detail at [knowledge/tooling/opencode/skills/dependency-checker.md](../../../knowledge/tooling/opencode/skills/dependency-checker.md). It is important to understand the boundary:

- **Plugin repository scanning** (this document): Targets `@runicengines/opencode-runesmith`'s own `package.json` and lockfile. Run in the plugin's CI pipeline.
- **Consumer scanning** (dependency-checker skill): Targets the consumer project's dependencies. Runs as an OpenCode skill on demand. Does not scan the plugin itself.

Both layers are necessary. The plugin's own scanning ensures the plugin is not distributing vulnerable code. The consumer scanning ensures the consumer's project is not vulnerable in its own dependencies.

### Recommended Composite Approach

```
Plugin Repository (this repo)
  └─ CI: npm audit --audit-level=high (every PR)
  └─ Dependabot alerts (continuous)
  └─ Manual: Review lockfile diffs in PRs
  └─ Release: Final audit before npm publish

Consumer Project (dev workstation)
  └─ OpenCode's dependency-checker skill (on demand)
  └─ npm audit (optional, developer choice)
  └─ Dependabot alerts (if consumer project is a GitHub repo)
```

---

## SBOM Considerations

### What Is an SBOM

A Software Bill of Materials (SBOM) is a formal, machine-readable inventory of all components in a software artifact. The two dominant standards are:

| Standard | Format | Key Feature |
|---|---|---|
| **CycloneDX** | JSON/XML | Designed for application security; supports vulnerability references, component pedigree, dependency graph |
| **SPDX** | JSON/YAML/RDF | Originated in licensing; broader scope including licenses, copyrights, security |

For a small npm plugin, CycloneDX is the more practical choice due to better npm ecosystem tooling and vulnerability reference integration.

### npm's Built-in SBOM Generation

npm provides a built-in SBOM command:

```bash
npm sbom
```

This generates a CycloneDX-formatted SBOM from the installed `node_modules` tree, using the lockfile for resolution. It captures:

- All direct and transitive dependencies
- Version numbers
- Package integrity hashes
- License information (from `package.json` `license` field)

### When to Generate

Generate an SBOM for every release:

| Event | Action |
|---|---|
| Before publishing a new version | Run `npm sbom` and include output in release artifacts |
| On security audit (post-release) | Regenerate SBOM from the tag's lockfile for analysis |

### Where to Publish

For a small internal plugin, the SBOM should be attached to each GitHub Release:

1. Run `npm sbom --sbom-format=cyclonedx > sbom.cyclonedx.json`
2. Attach `sbom.cyclonedx.json` to the GitHub Release
3. (Optional) Upload as a CI artifact for traceability

### Practical Recommendation for RuneSmith

Given the plugin's minimal dependency tree (one direct production dependency), an SBOM adds limited practical value today. The recommendation is tiered:

| Phase | Action |
|---|---|
| **Now** | Generate SBOM manually before releases. Store in release artifacts. |
| **If dependency count grows** | Automate SBOM generation in the release CI workflow. Upload as release asset. |
| **If compliance requirements emerge** | Adopt CycloneDX formally, integrate with vulnerability scanning tooling. |

For context, an SBOM for the current plugin would contain approximately 3-5 entries (one direct dependency + its transitive dependencies). The value scales with dependency count.

---

## Recommended Approach

### Summary of Recommendations (Priority Order)

| Priority | Recommendation | Category | Effort |
|---|---|---|---|
| P0 | Commit `package-lock.json` and use `npm ci` in CI | Pinning | 5 min |
| P0 | Enable Dependabot alerts on the plugin repository | Scanning | 2 min |
| P0 | Add `npm audit --audit-level=high` to CI for every PR | Scanning | 15 min |
| P1 | Pin `@opencode-ai/plugin` to exact version in `package.json` | Pinning | 2 min |
| P1 | Configure `.github/dependabot.yml` for weekly npm updates | Pinning | 10 min |
| P1 | Review lockfile diffs in PRs as part of code review process | Process | Ongoing |
| P2 | Generate CycloneDX SBOM before each release | SBOM | 5 min per release |
| P2 | Attach SBOM to GitHub Release artifacts | SBOM | 2 min per release |
| P3 | Automate SBOM generation in release CI workflow | SBOM | 1 hour |
| P3 | Enable GitHub Dependency Graph for the repository | Scanning | 2 min |

### Implementation Checklist

Use this checklist when setting up or auditing the plugin repository's security posture:

- [ ] `package-lock.json` is committed to the repository
- [ ] CI runs `npm ci` (not `npm install`)
- [ ] CI runs `npm audit --audit-level=high` and fails on high/critical findings
- [ ] Dependabot alerts are enabled in repository settings
- [ ] `.github/dependabot.yml` is configured with weekly schedule
- [ ] Production dependencies use exact version pins in `package.json`
- [ ] DevDependencies use semver ranges (e.g., `^` or `~`)
- [ ] Lockfile diffs are reviewed in PRs as part of standard review
- [ ] SBOM is generated before each release (manual or automated)
- [ ] SBOM is attached to each GitHub Release
- [ ] Plugin maintainers have 2FA enabled on their GitHub accounts
- [ ] Consumer `.npmrc` is documented with correct registry and token setup
