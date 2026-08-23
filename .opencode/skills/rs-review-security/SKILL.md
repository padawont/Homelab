---
name: rs-review-security
description: >
  Perform deep security code review across 6 domains (injection, auth,
  authorization, data exposure, dependencies, cryptography) with OWASP
  Top 10 mapping and remediation guidance.
license: MIT
compatibility: opencode
metadata:
  plugin: "@runicengines/opencode-runesmith"
  workflow: planning
  audience: developers
  trigger: chained
---

## Purpose

Conduct a thorough security review of pull request code changes across 6 security domains. Maps each finding to the OWASP Top 10 (2021) category, assigns a risk level (critical/high/medium/low), and provides remediation recommendations.

## When to Invoke

- rs-review-methodology chains this skill for full or security review types.
- A PR involves authentication, authorization, or data handling.
- The user explicitly requests a security review.

Do NOT invoke when:

- The PR contains no code changes (e.g., documentation-only PR).
- Security review has already been performed and cached.

## 6-Domain Checklist

| #   | Domain         | Focus Areas                                                                                       |
| --- | -------------- | ------------------------------------------------------------------------------------------------- |
| 1   | Injection      | SQL, NoSQL, command, LDAP, template injection — parameterised queries, escaping, input validation |
| 2   | Authentication | Password handling, session management, MFA, token validation, OAuth flows                         |
| 3   | Authorization  | Role checks, permission enforcement, ACLs, privilege escalation paths                             |
| 4   | Data Exposure  | PII logging, verbose error messages, API response over-fetching, encryption at rest/transit       |
| 5   | Dependencies   | Known CVEs, unpinned versions, abandoned packages, typosquatting risks                            |
| 6   | Cryptography   | Weak algorithms (MD5, SHA1, RC4), hardcoded keys, key rotation, entropy sources                   |

## OWASP Top 10 (2021) Mapping

| OWASP Category                   | Domains                     |
| -------------------------------- | --------------------------- |
| A01 Broken Access Control        | Authorization               |
| A02 Cryptographic Failures       | Cryptography, Data Exposure |
| A03 Injection                    | Injection                   |
| A04 Insecure Design              | All domains                 |
| A05 Security Misconfiguration    | Dependencies, Cryptography  |
| A06 Vulnerable Components        | Dependencies                |
| A07 Identification/Auth Failures | Authentication              |
| A08 Software/Data Integrity      | Dependencies                |
| A09 Security Logging Failures    | Data Exposure               |
| A10 SSRF                         | Injection                   |

## Workflow Steps

### 1. Review injection domain

Scan for unsanitized user input in SQL queries, shell commands, template engines, and LDAP queries.

### 2. Review authentication domain

Inspect auth flows, token handling, session management, password storage.

### 3. Review authorization domain

Verify role checks, permission enforcement, access control lists.

### 4. Review data exposure domain

Check for PII in logs, verbose errors, excessive API responses, missing encryption.

### 5. Review dependencies domain

Audit dependency manifests for known CVEs, unpinned versions, outdated packages.

### 6. Review cryptography domain

Inspect algorithm choices, key management, random number generation.

### 7. Generate security report

Produce structured YAML with findings per domain, OWASP mapping, risk levels, and remediation.

## Output Format

```yaml
security_review:
  domains:
    injection:
      status: pass
      findings: []
    authentication:
      status: fail
      findings:
        - domain: authentication
          owasp: A07
          risk: high
          file: src/auth.py
          line: 85
          description: JWT secret hardcoded in source
          remediation: Use environment variable or secrets manager
  summary:
    total_findings: 3
    critical: 0
    high: 1
    medium: 1
    low: 1
    verdict: changes-requested
```

## Required Permissions

| Tool  | Required | Scope                   | Purpose                        |
| ----- | -------- | ----------------------- | ------------------------------ |
| read  | Yes      | Source files, manifests | Read code and dependency files |
| grep  | Yes      | Source tree             | Search for security patterns   |
| bash  | Yes      | git                     | Get PR diff                    |
| edit  | No       | —                       | Read-only review skill         |
| write | No       | —                       | Read-only review skill         |

## Chained Skills

| Skill              | When to Chain                  |
| ------------------ | ------------------------------ |
| rs-review-severity | Every finding — classify S1–S5 |

## See Also

- rs-review-methodology — parent orchestrator
- rs-review-severity — severity classification
- OWASP Top 10 (2021) — https://owasp.org/Top10/
