# NixOS

Reference notes on [NixOS](https://nixos.org/) — a Linux distribution built on the Nix package manager, featuring declarative configuration, atomic upgrades, and rollback.

## Files

| File | Description |
|---|---|
| [what-is-nixos.md](what-is-nixos.md) | Declarative OS model, Nix language, generations, Nix store |
| [nixos-configuration.md](nixos-configuration.md) | /etc/nixos layout, configuration.nix, hardware-configuration.nix, flakes, rebuild workflow |
| [rollback-mechanisms.md](rollback-mechanisms.md) | Boot generations, nixos-rebuild --rollback, garbage collection |
| [installation.md](installation.md) | ISO installation, disko partitioning, nixos-install workflow |
| [secrets-management.md](secrets-management.md) | sops-nix, agenix, password hashing |
