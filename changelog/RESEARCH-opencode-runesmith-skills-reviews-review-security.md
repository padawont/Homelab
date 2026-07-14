---
title: "Review Security Skill Design"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - skills
  - review
  - security
  - runesmith
sources:
  - knowledge: "knowledge/tooling/opencode/skills/overview.md"
references:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-06-07
---

# Review Security Skill Design

## Context

The `@runicengines/opencode-runesmith` plugin provides OpenCode agents with RunicEngines-specific skill workflows. The `rs-review-security` skill is a review skill — it provides security-specific review patterns that help the reviewer agent identify common vulnerabilities during code review. It is designed to be loaded on-demand when the code under review touches security-sensitive areas such as authentication, cryptography, secrets management, data validation, or authorization logic.

This file is a research analysis: it documents the skill's design requirements, its recommended instruction body, and maps the security patterns it should flag. It also clarifies the relationship between `rs-review-security` and sibling skills `rs-review-methodology` (which should be loaded first) and `rs-dependency-checker` (for dependency vulnerability scanning).

### Why a Separate Security Review Skill?

Generic code review catches logic errors, style violations, and readability issues — but security vulnerabilities require specialized knowledge: injection vectors, cryptographic pitfalls, authorization bypasses, and secret leakage. By isolating security review into its own skill, the reviewer agent can load it only when needed, keeping the review focused and the agent's context window uncluttered. It follows the on-demand loading pattern established by other RunicEngines skills.

### Skill Identity

| Property | Value |
|---|---|
| Plugin | `@runicengines/opencode-runesmith` |
| Skill name | `rs-review-security` |
| Skill prefix | `rs-` |
| Loading model | On-demand (via `skill({ name: "rs-review-security" })`) |
| Primary user | Reviewer agent |
| Secondary user | Developer agent (self-review) |
| Trigger | Code changes involving auth, crypto, secrets, data validation, or security-sensitive configuration |

---

## Recommended SKILL.md Instructions

The following block is the recommended instruction body for the skill's `SKILL.md` file. It defines the security review methodology, the vulnerability checklist, automatic flag patterns, and output format conventions.

```markdown
---
name: rs-review-security
description: >
  Security-specific code review patterns for the reviewer agent.
  Identifies injection flaws, auth weaknesses, crypto missteps,
  secret leakage, and authorization gaps.
license: MIT
compatibility: opencode
metadata:
  workflow: review
  audience: reviewer
  trigger: conditional
---

# rs-review-security

## Purpose

Provides security-specific review patterns that help the reviewer agent
identify common vulnerabilities in code changes. This skill is loaded
when the code under review touches security-sensitive areas such as
authentication, cryptography, secrets management, data validation, input
sanitization, or authorization logic. It supplements the general review
patterns from `rs-review-methodology` with a focused security lens.

## When to Invoke

- The code under review includes authentication or session management.
- The code under review handles cryptographic operations.
- The code under review processes secrets, tokens, API keys, or passwords.
- The code under review performs input validation or data sanitization.
- The code under review modifies security configuration (TLS, CORS, CSP,
  rate limiting, access control lists).
- The diff contains references to security libraries, encryption functions,
  or authorization primitives.
- The diff introduces new dependencies or updates existing ones.

## Trigger

| Condition | Type |
|---|---|
| Reviewer detects security-sensitive code in diff | Conditional (manual) |
| Code touches `auth`, `crypto`, `secret`, `password`, `token`, `permission`, `acl`, `cors`, `csrf`, `xss`, `sql`, `injection`, `sanitize`, `validate` | Auto-suggest |
| Dependency changes are present in the diff | Auto-suggest |

## Required Permissions

| Permission | Purpose |
|---|---|
| `read` | Read code diffs, configuration files, dependency manifests |
| `grep` | Search for security-sensitive patterns in changed files |
| `glob` | Find files matching security-relevant patterns (e.g. `*secret*`, `*auth*`, `*crypto*`) |

The `rs-review-methodology` skill should be loaded first via
`skill({ name: "rs-review-methodology" })` to establish the base
review process. This skill adds the security layer on top.

## Input

The skill operates on the same code changes provided to the reviewer
agent, supplemented by optional **security context** — metadata that
identifies which security domains are in scope:

```
Security Context:
  domains: [authentication, authorization, cryptography, secrets, data-validation]
  sensitive_files: [src/auth/, config/secrets/, src/crypto/]
  threat_model_available: true | false   # link if available
```

If no explicit security context is provided, the skill auto-detects
relevant domains by scanning the diff for security-related keywords.

## Security Checklist

For each domain in scope, run the corresponding checks:

### Injection

| Check | What to look for |
|---|---|
| SQL injection | String concatenation in SQL queries, raw `.execute()` with f-strings, missing parameterized queries |
| Command injection | `os.system()`, `subprocess.run(shell=True)`, `exec()`, `eval()` with user input |
| Template injection | User input passed to template engines without escaping (Jinja2, Handlebars, etc.) |
| NoSQL injection | Unsanitized user input in MongoDB `$where`, `$regex`, or query objects |
| LDAP injection | User input in LDAP filter strings without sanitization |
| Path traversal | User input used in file path construction without normalization checks |

**Examples:**
```python
# VULNERABLE: SQL injection via f-string
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")

# SAFE: parameterized query
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
```

### Authentication

| Check | What to look for |
|---|---|
| Token handling | JWTs stored in localStorage, missing expiry validation, hardcoded `secretOrPrivateKey` |
| Session management | Predictable session IDs, missing `httpOnly`/`secure` cookie flags, session fixation |
| Password storage | Plaintext storage, weak hashing (MD5, SHA-1 without salt), missing bcrypt/argon2 |
| Password policies | Missing minimum length/complexity checks, no rate limiting on login |
| MFA | Missing multi-factor on privileged actions, bypassable MFA checks |
| Reset flows | Predictable reset tokens, token leak in URL params, no expiry on reset links |

**Examples:**
```javascript
// VULNERABLE: Hardcoded JWT secret
const token = jwt.sign({ userId: user.id }, 'super-secret-key');

// SAFE: Secret from environment variable
const token = jwt.sign({ userId: user.id }, process.env.JWT_SECRET);
```

### Authorization

| Check | What to look for |
|---|---|
| Access control | Missing authorization checks on API endpoints, IDOR vulnerabilities |
| Privilege escalation | Users can elevate to admin, missing role verification on sensitive actions |
| Horizontal escalation | User A can access User B's resources by changing an ID parameter |
| RBAC gaps | Missing or incorrect role/permission checks in middleware or guards |
| CORS misconfiguration | Overly permissive `Access-Control-Allow-Origin: *` on authenticated endpoints |

**Examples:**
```javascript
// VULNERABLE: No authorization check — any user can access any profile
app.get('/api/users/:id/profile', (req, res) => {
  const profile = db.getUserProfile(req.params.id);
  res.json(profile);
});

// SAFE: Check that the requesting user owns the resource
app.get('/api/users/:id/profile', authenticate, (req, res) => {
  if (req.user.id !== req.params.id && req.user.role !== 'admin') {
    return res.status(403).json({ error: 'Forbidden' });
  }
  const profile = db.getUserProfile(req.params.id);
  res.json(profile);
});
```

### Data Exposure

| Check | What to look for |
|---|---|
| Secrets in logs | `console.log()`, `logger.info()` printing passwords, tokens, keys |
| Secrets in env files | `.env` committed to version control, secrets in config files |
| Secrets in error messages | Stack traces or internal state exposed in HTTP responses |
| Hardcoded credentials | API keys, database passwords, secret keys in source code |
| PII leakage | Personal data in URLs, response bodies, or logs without redaction |
| Verbose error handling | Detailed error messages leaking schema, internals, or debug info |

**Examples:**
```python
# VULNERABLE: Token printed in log
logger.info(f"User {email} authenticated with token: {token}")

# SAFE: Log without sensitive data
logger.info(f"User {email} authenticated successfully")
```

### Dependencies

| Check | What to look for |
|---|---|
| Known vulnerabilities | Dependencies with known CVEs — delegate full scan to `rs-dependency-checker` |
| Deprecated packages | Use of unmaintained or end-of-life libraries |
| Unpinned versions | Floating version ranges (`^1.0.0`, `>=2.0`) that may pull in vulnerable versions |
| Transitive risk | Dependencies with large dependency trees that increase attack surface |

**Note:** This skill flags suspicious dependency changes but does **not**
perform a full vulnerability scan. Delegate that to `rs-dependency-checker`
via `skill({ name: "rs-dependency-checker" })`.

### Cryptography

| Check | What to look for |
|---|---|
| Weak algorithms | MD5, SHA-1, DES, RC4, ECB mode for block ciphers |
| Custom crypto | Home-grown encryption, custom hash functions, non-standard protocols |
| Poor key management | Hardcoded keys, keys derived from passwords without KDF, insufficient key length |
| Weak TLS | TLS 1.0/1.1 enabled, weak cipher suites, missing certificate pinning |
| Randomness | Use of `Math.random()` or `random` module for security contexts (use `crypto.randomBytes` or `secrets` instead) |
| Padding oracle | Missing authenticated encryption (use AES-GCM or ChaCha20-Poly1305, not AES-CBC alone) |

**Examples:**
```go
// VULNERABLE: Weak hash for password storage
hash := md5.Sum([]byte(password))

// SAFE: bcrypt with work factor
hash, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
```

## Patterns to Flag Automatically

Search the diff for these patterns and flag each as a security finding.
Do not rely on exact string matching — use semantic understanding of the
code's purpose in addition to regex-based pattern detection.

| Pattern | Risk Level | What it indicates |
|---|---|---|
| Hardcoded secret, key, or token string literal (looks like `sk-...`, `-----BEGIN`, `password = "..."`, `api_key = "..."`) | Critical | Credential leakage — secret is visible in source code |
| Raw SQL string concatenation (`"SELECT * FROM " +`, `f"SELECT {`) | Critical | SQL injection vulnerability |
| Missing input validation on user-controlled data | High | Injection, XSS, or data corruption risk |
| `shell=True` in subprocess calls | High | Command injection risk |
| Security check disabled (`verify=False`, `check=False`, `NODE_TLS_REJECT_UNAUTHORIZED=0`, `secure: false`) | Critical | Security controls explicitly bypassed — likely for testing, left in production |
| Weak TLS/SSL config (`ssl_version=PROTOCOL_TLSv1`, `ciphers='DEFAULT'` with weak suites) | High | Insecure transport — data can be intercepted |
| `eval()` / `exec()` with non-literal input | High | Arbitrary code execution risk |
| Cookie missing `httpOnly` or `secure` flag | Medium | Session token can be read by JavaScript or sent over HTTP |
| CORS wildcard with credentials (`Access-Control-Allow-Origin: *` + `Access-Control-Allow-Credentials: true`) | High | Cross-origin credential leakage |
| Unpinned dependency version (`"express": "^4.0.0"`) | Low | Supply chain risk — may pull in vulnerable versions |
| `pickle.loads()` / `yaml.load()` (without safe loader) | High | Deserialization vulnerability |
| User input in file path (`open(user_input,`) without normalization | High | Path traversal risk |

## Finding Report Format

Each security finding must include these four fields:

```markdown
### Finding: {short name}

- **File:** `path/to/file.ext` (line N)
- **Risk Level:** {Critical | High | Medium | Low}
- **Description:** {clear, non-technical explanation of the vulnerability
  and its potential impact}
- **Remediation:** {specific, actionable suggestion for fixing the issue}
```

**Examples:**

```markdown
### Finding: Hardcoded JWT Secret

- **File:** `src/auth/token.js` (line 15)
- **Risk Level:** Critical
- **Description:** The JWT signing secret is hardcoded as a string literal
  in the source code. Anyone with access to this repository can forge
  valid JWTs, impersonate any user, and gain unauthorized access.
- **Remediation:** Move the secret to an environment variable
  (`process.env.JWT_SECRET`) and ensure it is set in production via a
  secrets manager. Rotate the compromised secret immediately.

### Finding: SQL Injection in User Lookup

- **File:** `src/api/users.js` (line 42)
- **Risk Level:** Critical
- **Description:** User input (`req.query.email`) is concatenated directly
  into a SQL query string. An attacker can craft a malicious email value
  that alters the query's logic, potentially bypassing authentication or
  exfiltrating data.
- **Remediation:** Replace f-string interpolation with a parameterized
  query using `?` or `%s` placeholders, or use an ORM that handles
  escaping automatically.

### Finding: Weak Password Hash

- **File:** `src/auth/register.py` (line 28)
- **Risk Level:** High
- **Description:** Passwords are hashed with MD5, which is vulnerable to
  collision attacks and can be cracked in seconds with consumer hardware.
  An attacker who gains access to the password database can recover
  plaintext passwords rapidly.
- **Remediation:** Replace MD5 with bcrypt (cost factor >= 12) or Argon2id
  using a well-audited library like `bcrypt` or `argon2-cffi`.
```

## Chained Skills

| Skill | Condition | Purpose |
|---|---|---|
| `rs-review-methodology` | Always — load first | Establishes base review process, diff parsing, and output conventions |
| `rs-dependency-checker` | When dependency changes are detected | Performs full CVE scan on changed dependencies |

Chained skills are loaded via `skill({ name: "..." })` and execute
independently. The reviewer agent coordinates results from all loaded
skills into a unified review output.

## Output

The skill produces a list of security findings in the format described
above. Each finding includes a file location, risk level, description,
and remediation suggestion. The reviewer agent integrates these findings
into the overall review response alongside findings from
`rs-review-methodology` and any other loaded review skills.

## See Also

- [rs-review-methodology](/research/opencode-runesmith/skills/reviews/review-methodology/) — Base review process (load first)
- [rs-dependency-checker](/research/opencode-runesmith/skills/utilities/dependency-checker/) — Dependency vulnerability scanning
- [OpenCode Skills Documentation](https://opencode.ai/docs/skills)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/) — Industry standard web application security risks
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/) — Security best practices reference
```

---

## Design Decisions

**1. On-demand, conditional loading.** The skill is loaded via `skill({ name: "rs-review-security" })` only when the diff touches security-sensitive code. This avoids bloating the reviewer agent's context window with security patterns during every review. The auto-suggest trigger conditions (keyword matching across the diff) let the agent proactively offer security review without the user explicitly requesting it.

**2. rs-review-methodology as a prerequisite.** Security review is a specialized layer on top of general review. By requiring `rs-review-methodology` to load first, the reviewer agent always has the base review process established — diff parsing conventions, general code quality checks, and output formatting — before adding the security lens. This prevents duplication of review infrastructure across skills.

**3. Separation from dependency scanning.** Dependency vulnerability scanning (`rs-dependency-checker`) is a separate skill because it has fundamentally different mechanics: it requires network access (CVE database queries) and package manifest parsing rather than source code analysis. The security review skill flags suspicious dependency changes but delegates the full scan to `rs-dependency-checker`, keeping responsibilities cleanly separated.

**4. Finding format with risk levels.** Every finding includes a risk level (Critical/High/Medium/Low) so the developer can prioritize remediation. Critical findings (hardcoded secrets, disabled security checks) should block merge; High findings (injection risks, weak crypto) should require remediation before merge; Medium/Low findings should be documented for the backlog.

**5. Examples in checklist items.** Each checklist domain includes before/after code examples. This is essential for the agent: LLM-based reviewers understand concrete examples better than abstract rules. The examples also serve as few-shot prompts for finding format, risk level calibration, and remediation specificity.

**6. Semantic pattern matching over regex.** The "Patterns to Flag Automatically" section explicitly instructs the agent to use semantic understanding in addition to pattern detection. Hardcoded secrets, for instance, can appear in many syntactic forms — a regex-only approach would miss strings constructed from parts or secrets loaded from seemingly unrelated variables. The agent should use its code understanding to infer what constitutes a secret, not just match literal strings.

## Risk Assessment

**False positives in auto-triggering.** Keyword-based auto-suggest may trigger the security review skill when a diff merely references a security library without changing security-sensitive logic (e.g., importing `crypto` for non-security UUID generation). The agent should evaluate the diff first before declaring a full security review — keyword matches are a suggestion, not a mandate.

**Overwhelming finding volume.** Applying the full security checklist to a large diff could produce dozens of findings, many of which may be low-significance. The skill should prioritize findings by risk level and, for large diffs, summarize low-risk patterns rather than listing each instance individually.

**Stale vulnerability data.** The dependency checks rely on CVE databases that change daily. The skill recommends delegating to `rs-dependency-checker` for this reason — keeping CVE data current is a separate concern from code analysis. The security review skill's dependency section should flag only obvious patterns (e.g., deprecated packages, unpinned versions) and leave deep scanning to the dedicated skill.

**TLS configuration context.** Weak TLS config flags may be false positives in internal-only services or development environments. The skill should note the environment context when flagging TLS issues, and the finding should include a note about when the configuration is acceptable.

## Recommendations

1. **Integrate with threat model documents.** When a threat model exists for the project being reviewed, the skill should reference it to scope the review — focusing on the threats identified rather than running the full checklist. This makes reviews faster and more relevant.

2. **Add a "security debt" output section.** In addition to individual findings, the skill should produce a summary section that tracks recurring security patterns across reviews — e.g., "3 out of 5 recent reviews found hardcoded secrets in this project." Over time, this becomes a security debt metric that the team can track.

3. **Support review annotations in PR comments.** The finding format is designed for human reading, but the skill could optionally output findings as GitHub PR review comments (with `path`, `line`, `body` fields) for direct integration with the PR workflow. This bridges the gap between agent-generated reviews and the GitHub review UI.

4. **Create a security baseline config.** The skill should accept an optional configuration file (`.runesmith/security.yml`) that defines project-specific overrides — allowed cryptographic algorithms, known-safe patterns to ignore, custom threat models to reference. This lets projects customize the security posture without modifying the skill itself.

---

## See Also

- [Research: Review Methodology Skill](/research/opencode-runesmith/skills/reviews/review-methodology/) — Base review process that loads this skill for security-sensitive code
- [Research: Dependency Checker Skill](/research/opencode-runesmith/skills/utilities/dependency-checker/) — Separate skill for CVE-based dependency scanning
- [Knowledge: OpenCode Skills Overview](/knowledge/tooling/opencode/skills/overview/) — OpenCode skill system reference
- [OWASP Top 10 (2021)](https://owasp.org/www-project-top-ten/) — Industry standard for web application security risks
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/) — Comprehensive security best practices
- [OpenCode Skills Documentation](https://opencode.ai/docs/skills) — Official OpenCode docs on skill authoring
