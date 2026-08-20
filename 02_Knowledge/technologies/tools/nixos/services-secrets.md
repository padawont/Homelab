---
title: "NixOS services and secrets management"
status: accepted
author: "padawont"
date: 2026-08-20
tags: [nixos, systemd, secrets, agenix, sops-nix]
sources:
  - url: "https://github.com/ryantm/agenix"
    title: "agenix"
  - url: "https://github.com/Mic92/sops-nix"
    title: "sops-nix"
last_audit_date: 2026-08-20
related_docs:
  - "./02_Knowledge/technologies/tools/nixos/overview.md"
  - "./02_Knowledge/technologies/tools/nixos/flakes.md"
  - "./05_Implementations/node-main/nixos/"
---

# NixOS services and secrets management

## Overview

On NixOS, services are declared declaratively as systemd units, and secrets are handled at activation time rather than living in the store. This note covers declaring services and the two common secret managers for the homelab migration: agenix and sops-nix.

## Details

### Declaring services

NixOS modules wrap systemd, so most services are enabled via `services.<name>` options. For custom daemons, define a unit directly:

Example — abstract:

```nix
{ config, pkgs, ... }:
{
  systemd.services.node-exporter = {
    wantedBy = [ "multi-user.target" ];
    serviceConfig = {
      ExecStart = "${pkgs.prometheus-node-exporter}/bin/node_exporter";
      Restart = "on-failure";
    };
  };
}
```

Useful attributes: `wantedBy`, `after`, `script`/`serviceConfig.ExecStart`, `environment`, `restartIfChanged`. Secrets referenced by a unit's `environment` or `ExecStart` come from the secret managers below.

### Why secrets need special handling

Files added to the Nix store are world-readable and persist in `/nix/store` across generations. Secret managers instead keep ciphertext in the repo and decrypt it to a private path (e.g. `/run/secrets/`) only during activation.

### agenix

- Age-encrypted files (`secrets/foo.age`), one file per secret, committed to the repo
- Decrypted at activation into `/run/agenix/foo` using host age keys
- Configured in the NixOS module:

Example — abstract:

```nix
{ config, ... }:
{
  age.secrets.foo = {
    file = ../secrets/foo.age;
    owner = "admin";
  };
}
```

- Age keys: by default agenix uses the host's SSH host key as its identity — available when `services.openssh.enable` is set, exposing `/etc/ssh/ssh_host_ed25519_key` — so secrets encrypted for that host are decrypted during activation. `age-keygen -o key.txt` is only needed for non-SSH age keys; operators encrypt with the target host's public key.

### sops-nix

- One SOPS-encrypted file (typically YAML, `secrets.yaml`) holding all secrets; secrets are encrypted once and unwrapped per host key
- sops-nix decrypts it into secrets at activation

Example — abstract:

```nix
{ config, ... }:
{
  sops.age.keyFile = "/etc/sops/key.txt";
  sops.secrets.foo = { };
  sops.templates.my-app-env.content = "TOKEN=${config.sops.placeholder.foo}";
}
```

- Keys: an age key (`sops.age.keyFile`) is registered as a decryption key; editing is done with the `sops` CLI against `secrets.yaml`.

### agenix vs sops-nix

| Criterion | agenix | sops-nix |
|---|---|---|
| Storage | One `.age` file per secret | One `secrets.yaml` per scope |
| Editing | `agenix -e secret.age` | `sops secrets.yaml` |
| Key mgmt | Host SSH/age key auto-discovered | `sops.age.keyFile` + registration, or SSH host-key derivation via `sops.age.sshKeyPaths` / auto-generated `sops.age.generateKey` |
| NixOS wiring | `age.secrets.*` | `sops.secrets.*` / `sops.templates.*` |
| K8s overlap | — | Likely overlaps with existing sops usage for k8s (to confirm in Research #27) |

The Research (#27) step selects which one the homelab adopts; this note documents both for comparison.

## Sources / Further Reading

- [agenix](https://github.com/ryantm/agenix)
- [sops-nix](https://github.com/Mic92/sops-nix)
- See `./02_Knowledge/technologies/tools/nixos/overview.md` for how modules compose services into the system, and `./02_Knowledge/technologies/tools/nixos/flakes.md` for flake input pinning in general (e.g. home-manager). Flake-input setup for agenix/sops-nix is in each tool's upstream README and should be captured in Research #27.
