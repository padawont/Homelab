---
title: "DNS for Services and Pods"
status: draft
author: padawont
date: 2026-06-18
tags:
  - kubernetes
  - networking
  - dns
  - coredns
sources:
  - url: "https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/"
    title: "DNS for Services and Pods — Kubernetes Documentation"
last_audit_date: 2026-06-18
---

# DNS for Services and Pods

## Overview
Kubernetes runs a DNS service (typically CoreDNS) that assigns DNS names to Services and pods, enabling service discovery within the cluster. Every Service gets a DNS record. Pods can optionally get DNS records based on their hostname.

## CoreDNS
CoreDNS is the default cluster DNS provider since Kubernetes 1.13. It runs as a deployment with a ConfigMap for configuration. It watches Services and EndpointSlices from the API server and responds to DNS queries with the corresponding IP addresses.

## Service DNS Records
Services get A/AAAA records in the format: `<service>.<namespace>.svc.<cluster-domain>`. The default cluster domain is `cluster.local`. For headless Services, DNS returns the pod IPs directly instead of the Service IP.

## Pod DNS Records
Pods get DNS records only when `hostname` is set in the pod spec (or when using StatefulSets, which automatically assign hostnames). The format is: `<hostname>.<namespace>.svc.<cluster-domain>`.

## Search Domains
Pods are configured with a search domain list that allows short-form DNS queries. Default: `<namespace>.svc.<cluster-domain>`, `svc.<cluster-domain>`, `<cluster-domain>`. This is why `curl my-service` resolves without the full FQDN.

## Pod dnsPolicy
Four policies: `Default` (pod inherits the node's DNS resolution), `ClusterFirst` (default — cluster DNS first, falls back to node DNS), `ClusterFirstWithHostNet` (for pods using hostNetwork), `None` (use `dnsConfig` for full control).

## Custom DNS Config
`dnsConfig` in the pod spec allows custom nameservers, search domains, and options (e.g., `ndots:5`). This is used for stub domains, custom DNS servers, or alternative resolution order.

## References

- [DNS for Services and Pods — Kubernetes Documentation](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/)
- [Services](./services.md)
- [Pods](./pods.md)
