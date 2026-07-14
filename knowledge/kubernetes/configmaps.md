---
title: "ConfigMaps"
status: draft
author: padawont
date: 2026-06-18
tags:
  - kubernetes
  - configuration
  - configmaps
sources:
  - url: "https://kubernetes.io/docs/concepts/configuration/configmap/"
    title: "ConfigMaps — Kubernetes Documentation"
last_audit_date: 2026-06-18
---

# ConfigMaps

## Overview

A ConfigMap is an API object used to store non-confidential configuration data in key-value pairs. Pods can consume ConfigMaps as environment variables, command-line arguments, or configuration files via volume mounts. ConfigMaps are namespace-scoped.

## Creation Methods

ConfigMaps can be created from literal values (`kubectl create configmap --from-literal=key=value`), from files (`--from-file=config.properties`), from directories (`--from-file=config-dir/`), and from env files (`--from-env-file=app.env`).

## Environment Variable Injection

Use `valueFrom.configMapKeyRef` to inject a ConfigMap value as an environment variable. `configMapKeyRef.name` is the ConfigMap name, `configMapKeyRef.key` is the key, and `optional: true` makes the pod tolerate a missing ConfigMap.

## Volume Mounts

Mount a ConfigMap as a volume: each key becomes a file in the mount path, each value becomes the file content. `spec.containers[].volumeMounts[]` mounts the ConfigMap volume and `spec.volumes[]` defines the ConfigMap as a volume source. `items[]` can select specific keys.

## Immutable ConfigMaps

Setting `immutable: true` prevents changes to the ConfigMap after creation. This improves performance (no watch needed) and protects against accidental mutation. An immutable ConfigMap must be deleted and recreated to change values.

Cross-links: [Pods](./pods.md), [Secrets](./secrets.md).
