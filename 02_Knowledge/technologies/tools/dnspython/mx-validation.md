---
title: "dnspython — MX validation before sending mail"
status: draft
author: "padawont"
date: 2026-10-12
tags: [dnspython, dns, mx, email-validation, python]
sources:
  - url: "https://dnspython.readthedocs.io/en/stable/resolver-functions.html"
    title: "dnspython — Resolver Functions and The Default Resolver"
  - url: "https://dnspython.readthedocs.io/en/stable/resolver-class.html"
    title: "dnspython — Resolver and Answer classes"
  - url: "https://dnspython.readthedocs.io/en/stable/exceptions.html"
    title: "dnspython — Exceptions"
  - url: "https://dnspython.readthedocs.io/en/stable/resolver.html"
    title: "dnspython — Stub Resolver"
last_audit_date: 2026-10-12
related_docs:
  - "./05_Implementations/node-main/cv-sender/overview.md"
  - "./02_Knowledge/technologies/tools/python-email/smtp-sending.md"
---

# dnspython — MX validation before sending mail

## Overview

A domain can only receive mail if it publishes at least one **MX** (Mail
eXchanger) record. Before sending, a cheap pre-send check can ask DNS "does this
domain accept mail?" and skip the send when the answer is no.

This is a *deliverability* check, not a *syntax* check:

- **Syntax validation** answers "is `user@domain` well-formed?" — regex/parser
  only, no network.
- **MX validation** answers "does `domain` actually have a mail exchanger?" —
  requires a DNS lookup.

They are complementary. Run syntax first (free, local), then MX only for
addresses that pass, to avoid wasting an SMTP connection, bandwidth, and
reputation on addresses whose domain cannot receive mail.

## Details

`dns.resolver` exposes a module-level `resolve()` function that uses a default
resolver, and a `Resolver` class for a custom one. Prefer `resolve()`; the older
`query()` method is kept only for backwards compatibility. `resolve()` returns an `Answer` object, whose
entries are the answer records (`dns.rdtypes.ANY.MX.MX` for an MX query), each
with `preference` and `exchange` attributes.

### Example — abstract

```python
import dns.resolver

def domain_can_receive_mail(domain: str) -> bool:
    """True only if `domain` publishes at least one MX record."""
    try:
        answer = dns.resolver.resolve(domain, "MX")  # resolve(), not query()
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer,
            dns.resolver.NoNameservers, dns.resolver.LifetimeTimeout):
        return False
    # Answer is an rrset; iterate to inspect servers / preference.
    return any(rr.exchange for rr in answer)
```

### Reading the Answer rrset

```python
for rr in answer:
    print(rr.preference, rr.exchange)  # e.g. 10 mail.example.com.
```

Lower `preference` wins; a sending client normally tries the lowest first. For a
boolean pre-send gate only the presence of records matters — preference ordering
is the MTA's job, not the validator's.

### Exceptions to handle

All of these are `dns.resolver` exceptions (see `dns.exception` for the base
`Timeout`); catch them explicitly to convert DNS failures into a "cannot send"
decision instead of a crash:

| Exception | Meaning |
|---|---|
| `dns.resolver.NXDOMAIN` | Domain does not exist at all. |
| `dns.resolver.NoAnswer` | Domain exists but has no MX record. |
| `dns.resolver.NoNameservers` | No usable nameserver answered (all SERVFAIL/refused). |
| `dns.resolver.LifetimeTimeout` | Lookup exceeded the total lifetime budget. |

`NoAnswer` and `NXDOMAIN` are definitive "no mail"; `NoNameservers` and
`LifetimeTimeout` are transient resolver failures. Treating the transient cases
as "no mail" is the safe default for a pre-send gate, but if mail must not be
silently dropped, distinguish them and retry later instead.

### Custom resolver (optional)

To pin servers or set timeouts, construct a `Resolver` and call its `resolve()`:

```python
resolver = dns.resolver.Resolver(configure=False)
resolver.nameservers = ["10.0.0.53"]
resolver.lifetime = 5.0  # seconds; bounds LifetimeTimeout
answer = resolver.resolve(domain, "MX")
```

Note that a domain with no MX record may still receive mail if it has an
implicit fallback; that behaviour is governed by mail standards, not by DNS, so
an MX-only check is a conservative gate rather than a guarantee.

## Sources / Further Reading

- [dnspython — Resolver Functions and The Default Resolver](https://dnspython.readthedocs.io/en/stable/resolver-functions.html)
- [dnspython — Resolver and Answer classes](https://dnspython.readthedocs.io/en/stable/resolver-class.html)
- [dnspython — Exceptions](https://dnspython.readthedocs.io/en/stable/exceptions.html)
- [dnspython — Stub Resolver](https://dnspython.readthedocs.io/en/stable/resolver.html)
