# Kiwix

Kiwix is an offline reader for web content, optimized for Wikipedia and other ZIM-format content. It allows serving full offline copies of websites over HTTP without internet access.

This folder covers Kiwix server deployment and configuration for the homelab K3s cluster.

Status: completed

## Notes

- [what-is-kiwix.md](./what-is-kiwix.md) — Kiwix overview, ZIM format, and architecture
- [kiwix-serve-config.md](./kiwix-serve-config.md) — kiwix-serve Docker image configuration, ports, env vars, and volume setup
- [deploy-procedure.md](./deploy-procedure.md) — Step-by-step guide for deploying kiwix-serve on the K3s cluster

## Cross-References

- Kubernetes Deployments: [deployments.md](../deployments.md)
- Kubernetes Services: [services.md](../services.md)
- Kubernetes PersistentVolumeClaims: [storage.md](../storage.md)
- Kubernetes Jobs: [jobs.md](../jobs.md)
