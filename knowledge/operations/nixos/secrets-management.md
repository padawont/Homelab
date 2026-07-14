---
title: "Secrets Management"
status: draft
author: "padawont"
date: 2026-07-14
tags:
  - nixos
  - secrets
  - sops-nix
  - agenix
  - security
sources:
  - url: "https://github.com/Mic92/sops-nix"
    title: "sops-nix — Atomic secret provisioning for NixOS"
  - url: "https://github.com/ryantm/agenix"
    title: "agenix — age-encrypted secrets for NixOS"
last_audit_date: 2026-07-14
---

# Secrets Management

NixOS configurations are typically stored in version control and deployed from the Nix store, which is world-readable. Secrets (API keys, passwords, tokens) must be encrypted before being committed.

This note covers the two main secret management tools for NixOS: **sops-nix** and **agenix**.

## sops-nix

[sops-nix](https://github.com/Mic92/sops-nix) integrates [SOPS](https://github.com/mozilla/sops) with NixOS for atomic, declarative secret provisioning.

### How it works

- Secrets are encrypted in SOPS files (YAML, JSON, or binary)
- Decryption happens at activation time, not evaluation time
- Secrets are mounted to `/run/secrets/<name>` via a tmpfs
- Supports GPG keys or age keys for encryption
- SSH host keys can be converted to age keys for automatic decryption

### Setup with flakes

```nix
{
  inputs.sops-nix.url = "github:Mic92/sops-nix";
  inputs.sops-nix.inputs.nixpkgs.follows = "nixpkgs";

  outputs = { self, nixpkgs, sops-nix, ... }: {
    nixosConfigurations.myhost = nixpkgs.lib.nixosSystem {
      modules = [
        ./configuration.nix
        sops-nix.nixosModules.sops
      ];
    };
  };
}
```

### Configuration

```nix
{ config, pkgs, ... }: {
  sops = {
    # Default encrypted secrets file
    defaultSopsFile = ./secrets/secrets.yaml;

    # Automatically use SSH host keys for decryption (age format)
    age.sshKeyPaths = [ "/etc/ssh/ssh_host_ed25519_key" ];

    # Or use a dedicated age key
    # age.keyFile = "/var/lib/sops-nix/key.txt";
    # age.generateKey = true;

    # Secret definitions
    secrets = {
      # Simple secret — mounted at /run/secrets/my-password
      my-password = {};

      # Secret with custom permissions
      db-password = {
        owner = config.users.users.postgres.name;
        group = config.users.groups.postgres.name;
        mode = "0440";
      };

      # Secret from a different SOPS file
      api-token = {
        sopsFile = ./secrets/other-secrets.yaml;
        format = "yaml";
      };

      # Template (render content from placeholders)
      templates."app-config.env".content = ''
        DB_PASSWORD=${config.sops.placeholder.db-password}
        API_KEY=${config.sops.placeholder.api-key}
      '';
    };
  };
}
```

### Creating encrypted secrets

**1. Set up `.sops.yaml` at the repo root:**

```yaml
keys:
  - &admin_alice age1abc123...  # your age public key
  - &server_host age1xyz789...  # server's SSH key converted to age
creation_rules:
  - path_regex: secrets/.*\.yaml$
    key_groups:
    - age:
      - *admin_alice
      - *server_host
```

**2. Create a secret file:**

```console
# Create/edit an encrypted secret
$ nix-shell -p sops --run "sops secrets/secrets.yaml"
```

This opens `$EDITOR` with a YAML file. Example contents:

```yaml
my-password: super-secret-password
db-password: another-secret
api-token: tok-abc-123
```

**3. Update keys when adding new machines:**

```console
$ sops updatekeys secrets/secrets.yaml
```

### Accessing secrets at runtime

Secrets are decrypted to `/run/secrets/`:

```console
$ cat /run/secrets/my-password
super-secret-password
```

Reference them in configuration:

```nix
{ config, ... }: {
  users.users.alice.hashedPasswordFile = config.sops.secrets.my-password.path;
}
```

### Conversion: SSH host key to age

```console
# Convert a server's Ed25519 public key to an age key
$ nix-shell -p ssh-to-age --run 'ssh-keyscan myhost | ssh-to-age'
age1rgffpespcyjn0d8jglk7km9kfrfhdyev6camd3rck6pn8y47ze4sug23v3

# Convert a local key
$ nix-shell -p ssh-to-age --run 'cat /etc/ssh/ssh_host_ed25519_key.pub | ssh-to-age'
```

## agenix

[agenix](https://github.com/ryantm/agenix) is a simpler alternative using age directly.

### How it works

- Secrets are individual `.age` files — one file per secret
- Encrypted with SSH public keys (using `age` — no GPG)
- Decrypted during NixOS activation to `/run/agenix/`
- No separate `.sops.yaml` — public keys are listed in `secrets.nix`

### Setup with flakes

```nix
{
  inputs.agenix.url = "github:ryantm/agenix";

  outputs = { self, nixpkgs, agenix, ... }: {
    nixosConfigurations.myhost = nixpkgs.lib.nixosSystem {
      modules = [
        ./configuration.nix
        agenix.nixosModules.default
      ];
    };
  };
}
```

### Configuration

```nix
{ config, pkgs, ... }: {
  age.secrets = {
    secret1.file = ../secrets/secret1.age;
    secret2 = {
      file = ../secrets/secret2.age;
      path = "/etc/my-app/key";
      mode = "0600";
      owner = "my-service";
      group = "my-service";
    };
  };
}
```

Secrets are decrypted to `/run/agenix/<name>` by default.

### Creating encrypted secrets

**1. Create `secrets/secrets.nix` listing public keys:**

```nix
let
  alice = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIL0idNvgGiucWgup...";
  myserver = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPJDyIr/FSz1cJd...";
in {
  "db-password.age".publicKeys = [ alice myserver ];
  "api-token.age".publicKeys = [ alice myserver ];
}
```

**2. Encrypt a secret:**

```console
# Create and edit a new encrypted file
$ agenix -e secrets/db-password.age
```

**3. Rekey when keys change:**

```console
$ agenix --rekey
```

### Key differences from sops-nix

| Aspect | sops-nix | agenix |
|---|---|---|
| File format | YAML/JSON/binary (one file, many secrets) | Individual `.age` files (one file per secret) |
| Key management | `.sops.yaml` rules file | `secrets.nix` listing public keys |
| Encryption | SOPS (AES256-GCM) + age or GPG | age (X25519 + ChaCha20-Poly1305) |
| GPG support | Yes | No (SSH keys only) |
| Templates | Built-in (`sops.templates`) | Manual |
| Home manager | Via home-manager module | Via home-manager module |
| Maturity | More features, larger community | Simpler, less code |

## Password hashing

For user passwords, use hashed passwords in `configuration.nix`:

```console
# Generate a hashed password
$ mkpasswd -m sha-512
$y$j9T$WFoiErKnEnMcGq0ruQK4K.$4nJAY3LBeBsZBTYSkdTOejKU6KlDmhnfUV3Ll1K/1b.
```

In `configuration.nix`:

```nix
{ config, ... }: {
  users.users.alice = {
    isNormalUser = true;
    hashedPassword = "$y$j9T$WFoiErKnEnMcGq0ruQK4K.$4nJAY3LBeBsZBTYSkdTOejKU6KlDmhnfUV3Ll1K/1b.";
  };
}
```

For secrets-managed passwords (sops-nix):

```nix
{ config, ... }: {
  # Mark the secret as needed before user creation
  sops.secrets.my-password.neededForUsers = true;

  users.users.alice = {
    isNormalUser = true;
    hashedPasswordFile = config.sops.secrets.my-password.path;
  };
}
```

## Best practices

- **Never commit plaintext secrets** — always encrypt before committing
- **Store Age/GPG keys outside the repo** — use `~/.config/sops/age/keys.txt` or SSH host keys
- **Rotate secrets periodically** — especially for long-lived deployments
- **Use minimal permissions** — `mode = "0440"` or `"0400"`, specific owner/group
- **CI/CD handling** — inject decrypt keys via environment variables or SSH agent forwarding
- **Choose based on complexity** — agenix for simpler setups, sops-nix for multi-secret files and templates
