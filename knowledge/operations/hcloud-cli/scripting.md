---
title: "Scripting with hcloud CLI"
status: draft
author: "refactorartist"
date: 2026-07-11
tags:
  - hetzner
  - hcloud
  - scripting
  - automation
  - jq
  - api
sources:
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/guides/using-output-options.md"
    title: "Using Output Options — Guide"
    paragraph: "§JSON, §YAML, §Go Template Format, §noheader, §columns"
  - url: "https://docs.hetzner.cloud/"
    title: "Hetzner Cloud API Documentation"
    paragraph: "Rate limits, labels, naming conventions"
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud.md"
    title: "hcloud CLI Manual — Global Flags"
    paragraph: "§Options"
last_audit_date: 2026-07-11
---

# Scripting with hcloud CLI

The hcloud CLI supports structured output formats, making it suitable for scripting and automation with standard Unix tools.

## Output Formats

The `--output` (or `-o`) flag controls output format and is available on most commands:

| Format | Description |
|---|---|
| `table` | Default — human-readable table |
| `json` | JSON object/array — for programmatic consumption |
| `yaml` | YAML format |
| `columns=<fields>` | Custom table columns (e.g., `columns=id,name,status`) |
| `noheader` | Suppress table header — useful with columns |
| `format='{{.GoTemplate}}'` | Go template format using hcloud-go schema |

### JSON Output

```bash
# Single resource as JSON object
hcloud server describe my-server -o json

# List as JSON array
hcloud server list -o json
```

Source: [Using Output Options — JSON](https://github.com/hetznercloud/cli/blob/main/docs/guides/using-output-options.md)

### Custom Columns

```bash
# Show only specific columns
hcloud server list -o columns=id,name,status,ipv4

# Suppress header (useful for parsing)
hcloud server list -o noheader -o columns=id,name
```

Source: [Using Output Options — columns](https://github.com/hetznercloud/cli/blob/main/docs/guides/using-output-options.md)

### Go Template Format

```bash
hcloud location describe fsn1 -o format='{{.Name}} {{.City}}'
```

## jq Patterns

### Extracting Server IPs

```bash
# Get all server names and IPv4 addresses
hcloud server list -o json | jq '.[] | {name, ipv4: .public_net.ipv4.ip}'

# Get the first server's IPv4
hcloud server list -o json | jq -r '.[0].public_net.ipv4.ip'

# Get private network IP
hcloud server describe my-server -o json | jq -r '.private_net[0].ip'
```

### Filtering by Label

```bash
# List server names with env=production label
hcloud server list -o json | jq -r '.[] | select(.labels.env == "production") | .name'

# List servers without a label
hcloud server list -o json | jq -r '.[] | select(.labels.env == null) | .name'
```

### Filtering by Status

```bash
# Count servers by status
hcloud server list -o json | jq 'group_by(.status) | map({status: .[0].status, count: length})'
```

### Advanced Transformations

```bash
# Create a mapping of name → IP
hcloud server list -o json | jq 'map({(.name): .public_net.ipv4.ip}) | add'

# Filter by location and extract private IPs
hcloud server list -o json | jq '[.[] | select(.datacenter.location.name == "nbg1") | {name, private_ip: .private_net[0].ip}]'
```

## Batch Operations

### Processing All Servers

```bash
# Iterate over all server names and perform an action
for server in $(hcloud server list -o noheader -o columns=name); do
  hcloud server describe "$server" -o json | jq '{name: .name, status: .status}'
done
```

### Batch Delete with Filtering

```bash
# Delete all servers in a specific location
hcloud server list -o json | jq -r '.[] | select(.datacenter.location.name == "fsn1") | .name' |
while read -r name; do
  hcloud server delete "$name"
done
```

### Batch Snapshot Creation

```bash
# Snapshot all running servers with a specific label
hcloud server list -l env=staging -o json | jq -r '.[] | select(.status == "running") | .name' |
while read -r name; do
  hcloud server create-image --type snapshot --description "pre-update-$(date +%Y%m%d)" "$name"
done
```

## Context Automation

### Switching Contexts in Scripts

```bash
# Run commands against multiple projects
for ctx in production staging development; do
  echo "=== $ctx ==="
  hcloud context use "$ctx"
  hcloud server list -o columns=name,status
done
```

### Using Context Override (Non-Destructive)

The `--context` flag runs a single command with a different context without switching:

```bash
hcloud --context production server list
hcloud --context staging server list
```

### Context-Aware Scripts

```bash
#!/usr/bin/env bash
set -euo pipefail

CONTEXT="${HCLOUD_CONTEXT:-production}"

echo "Using context: $CONTEXT"
hcloud context use "$CONTEXT"

# List all servers with their IPs
hcloud server list -o json | jq -r '.[] | "\(.name): \(.public_net.ipv4.ip)"'
```

## Error Handling

### Exit Codes

The CLI returns standard exit codes:
- `0` — Success
- Non-zero — Error (command-specific)

```bash
# Check if a server exists
if hcloud server describe my-server > /dev/null 2>&1; then
  echo "Server exists"
else
  echo "Server does not exist"
fi
```

### Silent Mode

```bash
# Suppress all output except errors
hcloud --quiet server delete my-server
```

## Environment Variables

### HCLOUD_TOKEN

Set the token directly to bypass context configuration — useful for CI/CD, Docker, and one-off scripts:

```bash
# Set the token for the current shell session
export HCLOUD_TOKEN="<your-api-token>"
hcloud server list

# One-liner without persistent env var
HCLOUD_TOKEN="<token>" hcloud server create --name temp --type cx22 --image ubuntu-24.04
```

When `HCLOUD_TOKEN` is set, the CLI uses it directly and ignores the active context. If both token and context are available, the token takes precedence.

See [installation-auth.md](./installation-auth.md) for creating API tokens and setting up named contexts.

### HCLOUD_CONTEXT

Override the active context without changing the persisted configuration:

```bash
export HCLOUD_CONTEXT=production
hcloud server list
```

## Hetzner Cloud API Fundamentals

### Rate Limits

The Hetzner Cloud API enforces rate limits per project:
- **Default:** 3600 requests per hour per project
- **Refill:** Tokens refill gradually (1 per second for the default limit)
- **Burst:** Short bursts above the sustained rate are allowed
- **Limit headers:** `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset`
- **429 response:** `rate_limit_exceeded` error when limit is hit

Source: [Hetzner Cloud API — Rate Limits](https://docs.hetzner.cloud/)

For batch operations, add delays between iterations:

```bash
# Batch operation with rate limit awareness
for server in $(hcloud server list -l env=staging -o noheader -o columns=name); do
  hcloud server delete "$server"
  sleep 1  # Stay well within rate limits
done
```

### Resource Naming Conventions

- **Uniqueness:** Names must be unique per project
- **Server names:** Must be valid hostnames per RFC 1123
- **Labels:** Key-value pairs, max 63 chars per segment, `hetzner.cloud/` prefix reserved
- **Label selectors:** Support `==`, `!=`, `in()`, `notin()`, key presence

Source: [Hetzner Cloud API — Labels](https://docs.hetzner.cloud/)

### Poll-Interval for Async Operations

Some operations (create, delete) are asynchronous. Control polling frequency:

```bash
# Slow down polling for long operations
hcloud --poll-interval 2s server create --name my-server --type cx22 --image ubuntu-24.04
```

## Example: Provision a Server with Full Configuration

```bash
#!/usr/bin/env bash
set -euo pipefail

NAME="${1:-web-$(date +%s)}"
TYPE="${2:-cx22}"
IMAGE="${3:-ubuntu-24.04}"
LOCATION="${4:-nbg1}"

echo "Creating server: $NAME ($TYPE, $IMAGE, $LOCATION)"

# Create server
hcloud server create \
  --name "$NAME" \
  --type "$TYPE" \
  --image "$IMAGE" \
  --location "$LOCATION" \
  --ssh-key my-key \
  --label env=staging \
  --label project=openchoreo

# Get the IP
IP=$(hcloud server describe "$NAME" -o json | jq -r '.public_net.ipv4.ip')
echo "Server IP: $IP"
```

## Example: List All Resources by Project

```bash
#!/usr/bin/env bash
set -euo pipefail

contexts=(production staging development)

for ctx in "${contexts[@]}"; do
  echo ""
  echo "========================================"
  echo "  Project: $ctx"
  echo "========================================"

  hcloud --context "$ctx" server list -o json | jq -r '
    "Servers: \(length)",
    (.[] | "  - \(.name) (\(.status)) [\(.public_net.ipv4.ip)]")
  '
done
```
