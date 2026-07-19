# Research: Kiwix/Wikipedia Offline Server on K3s

## Issue Summary

**Goal:** Install `kiwix-serve` on the node-1 K3s cluster to serve Wikipedia offline via a LoadBalancer service at 192.168.111.101.

The deployment already has YAML manifests (`kiwix.yaml`, `kiwix-copy-job.yaml`) and knowledge notes in `knowledge/kubernetes/kiwix/`. This research validates the approach, checks documentation for accuracy, gathers current kiwix-serve upstream docs, and identifies any gaps before marking the work complete.

## Scope

- K3s single-node cluster on node-1 (192.168.111.10)
- `ghcr.io/kiwix/kiwix-serve` Docker image
- ZIM file management: copy job from host path to Longhorn PVC
- Kubernetes Service type LoadBalancer with static IP 192.168.111.101
- Service port 80 → container port 8080
- Liveness/readiness probes on `GET /`
- Hardware: ASUS ROG STRIX B550-I, Ryzen 7 5700G, 30 GB RAM, 954 GB Longhorn SSD

## Out of Scope

- High availability / multiple replicas
- Multi-language ZIM files (English Wikipedia only)
- BitTorrent-based ZIM download (manual host-path copy)
- Ingress/TLS termination (plain HTTP on LAN)
- Monitoring, metrics, or dashboard integration

---

## Knowledge Base References

### knowledge/kubernetes/kiwix/README.md

**chunk 1/1 (lines 1-16):**
```
1: # Kiwix
2:
3: Kiwix is an offline reader for web content, optimized for Wikipedia and other ZIM-format content. It allows serving full offline copies of websites over HTTP without internet access.
4:
5: This folder covers Kiwix server deployment and configuration for the homelab K3s cluster.
6:
7: ## Notes
8:
9: - [what-is-kiwix.md](./what-is-kiwix.md) — Kiwix overview, ZIM format, and architecture
10: - [kiwix-serve-config.md](./kiwix-serve-config.md) — kiwix-serve Docker image configuration, ports, env vars, and volume setup
11:
12: ## Cross-References
13:
14: - Kubernetes Deployments: [deployments.md](../deployments.md)
15: - Kubernetes Services: [services.md](../services.md)
16: - PersistentVolumeClaims: [storage.md](../storage.md)
```

---

### knowledge/kubernetes/kiwix/what-is-kiwix.md

**chunk 1/4 (lines 1-20):**
```
1: ---
2: title: "Kiwix"
3: status: draft
4: tags:
5:   - kiwix
6:   - offline
7:   - wikipedia
8:   - zim
9: sources:
10:   - url: "https://www.kiwix.org/en/"
11:     title: "Kiwix — Offline Browser"
12:   - url: "https://github.com/kiwix/kiwix-tools"
13:     title: "kiwix/kiwix-tools — GitHub"
14: last_audit_date: 2026-07-18
15: related_configs:
16:   - "configs/node-main/kubernetes/kiwix.yaml"
17: ---
18:
19: # Kiwix
20:
```

**chunk 2/4 (lines 21-40):**
```
21: ## Overview
22:
23: Kiwix is a free and open-source offline content browser. It reads ZIM files — highly compressed archives of web content — and serves them over HTTP so any device on the local network can access the content without an internet connection.
24:
25: Kiwix is primarily used to distribute Wikipedia offline, but it supports any content packaged in the ZIM format (Wiktionary, Wikisource, Stack Exchange dumps, TED talks, etc.).
26:
27: ## ZIM Format
28:
29: ZIM is an open file format designed for storing web content in a single compressed file. Key characteristics:
30:
31: - **Single file** — An entire website (thousands of pages, images, assets) is bundled into one `.zim` file
32: - **Compressed** — Uses zstd or xz compression; significantly reduces storage requirements
33: - **Random access** — Allows seeking into specific articles without decompressing the entire file
34: - **Metadata** — Stores title, language, date, creator, and description in the file header
35:
36: ZIM files are the standard format for Kiwix and are used by the offline Wikipedia distribution project.
37:
38: ## Wikipedia ZIM Files
39:
40: English Wikipedia is available in three variants from `download.kiwix.org/zim/wikipedia/`:
```

**chunk 3/4 (lines 41-60):**
```
41:
42: | Variant | Description | Approx Size |
43: |---|---|---|
44: | `maxi` | Full articles with images | ~115 GB |
45: | `nopic` | Full articles without images | ~45 GB |
46: | `mini` | Article introductions only | ~12 GB |
47:
48: ## Architecture
49:
50: Kiwix server (kiwix-serve) follows a simple architecture:
51:
52: ```
53: ┌─────────────┐     HTTP :8080
54: │  kiwix-serve │◄──────────────── Client browser
55: │  container   │
56: ├─────────────┤
57: │   /data/     │
58: │  *.zim files │
59: └─────────────┘
60: ```
```

**chunk 4/4 (lines 61-65):**
```
61:
62: - kiwix-serve is a single static binary that reads ZIM files and serves them over HTTP
63: - No database, no external dependencies
64: - All ZIM files in the `/data` directory are served automatically via globbing
65: - The service is stateless with respect to the binary — all state is in the ZIM files on the volume
```

---

### knowledge/kubernetes/kiwix/kiwix-serve-config.md

**chunk 1/5 (lines 1-20):**
```
 1: ---
 2: title: "kiwix-serve Configuration"
 3: status: draft
 4: tags:
 5:   - kiwix
 6:   - docker
 7:   - container
 8:   - configuration
 9: sources:
10:   - url: "https://github.com/kiwix/kiwix-tools/blob/main/docker/server/README.md"
11:     title: "kiwix-serve Docker Image — GitHub"
12:   - url: "https://kiwix-tools.readthedocs.io/en/stable/kiwix-serve.html"
13:     title: "kiwix-serve CLI Documentation"
14: last_audit_date: 2026-07-18
15: related_configs:
16:   - "configs/node-main/kubernetes/kiwix.yaml"
17: ---
18:
19: # kiwix-serve Configuration
20:
```

**chunk 2/5 (lines 21-40):**
```
21: ## Container Image
22:
23: The official kiwix-serve image is published at:
24:
25: ```
26: ghcr.io/kiwix/kiwix-serve
27: ```
28:
29: Tags: `latest`, `3.x.x` (semver). The image is multi-arch (amd64, arm64, arm32v7). Current release: 3.8.2 with libzim 9.5.0.
30:
31: ## Port
32:
33: kiwix-serve listens on TCP port **8080** by default. This is configurable via the `PORT` environment variable.
34:
35: ## Volume Mount
36:
37: ZIM files must be placed at `/data` inside the container. The directory is declared as a Docker `VOLUME` in the image.
38:
39: ## Command / Entrypoint
40:
```

**chunk 3/5 (lines 41-60):**
```
41: The image has ENTRYPOINT `["kiwix-serve", "--port=8080"]`. ZIM file paths are passed via CMD/args:
42:
43: ```
44: docker run ghcr.io/kiwix/kiwix-serve /data/file.zim
45: ```
46:
47: In Kubernetes, use `args:` (not `command:`) to pass ZIM files:
48:
49: ```yaml
50: args:
51: - /data/wikipedia_en_all_maxi_2025-08.zim
52: ```
53:
54: ## ZIM Format Compatibility
55:
56: kiwix-tools 3.8.2 (libzim 9.5.0) supports ZIM format v4 files but some newer ZIM files (mid-2025+) use a format version that this release considers invalid. To check compatibility, use `kiwix-manage add <file.zim>`. If it fails, use an older ZIM file (pre-2025).
57:
58: | ZIM File | Compatibility | Approx Size |
59: |---|---|---|
```

**chunk 4/5 (lines 61-80):**
```
61: | `wikipedia_en_all_maxi_2025-08.zim` | Compatible | ~115 GB |
62: | `wikipedia_en_all_maxi_2026-02.zim` | Incompatible | ~115 GB |
63: | `wikipedia_en_all_mini_2026-06.zim` | Incompatible | ~12 GB |
64:
65: ## Command-Line Flags
66:
67: Full reference at [kiwix-tools.readthedocs.io](https://kiwix-tools.readthedocs.io/en/stable/kiwix-serve.html):
68:
69: | Flag | Description |
70: |---|---|
71: | `--port`, `-p` | TCP port (default 80 CLI, 8080 in Docker) |
72: | `--address`, `-i` | Bind address |
73: | `--urlRootLocation`, `-r` | URL path prefix |
74: | `--threads`, `-t` | Number of concurrent request threads |
75: | `--library`, `-l` | Use library XML file instead of direct ZIM paths |
76: | `--skipInvalid`, `-k` | Start even if ZIM files are invalid (skips them) |
77: | `--verbose`, `-v` | Print debug log to STDOUT |
78:
79: ## Performance
80:
```

**chunk 5/5 (lines 81-93):**
```
81: - **Minimum RAM**: 256 MB (for small ZIM files under 1 GB)
82: - **Recommended RAM**: 1–2 GB (for full Wikipedia ~115 GB ZIM)
83: - **CPU**: single core sufficient; multi-core helps with concurrent requests
84: - **Threads**: Each additional thread consumes ~50 MB RAM. Default 4 threads is appropriate for most deployments.
85:
86: ## Health Checks
87:
88: kiwix-serve responds on `GET /` with HTTP 200 when running. Use this for liveness and readiness probes.
89:
90: ## ZIM File Management
91:
92: - kiwix-serve detects ZIM files at startup; files added or removed while running require a restart
93: - Multiple ZIM files in the same directory work — kiwix-serve presents a library page listing all available content
```

---

### configs/node-main/kubernetes/kiwix.yaml

**chunk 1/5 (lines 1-20):**
```
 1: ---
 2: apiVersion: v1
 3: kind: Namespace
 4: metadata:
 5:   name: kiwix
 6:
 7: ---
 8: apiVersion: v1
 9: kind: PersistentVolumeClaim
10: metadata:
11:   name: kiwix-data
12:   namespace: kiwix
13: spec:
14:   accessModes:
15:     - ReadWriteOnce
16:   storageClassName: longhorn
17:   resources:
18:     requests:
19:       storage: 150Gi
20:
```

**chunk 2/5 (lines 21-40):**
```
21: ---
22: apiVersion: apps/v1
23: kind: Deployment
24: metadata:
25:   name: kiwix
26:   namespace: kiwix
27:   labels:
28:     app: kiwix
29: spec:
30:   replicas: 1
31:   selector:
32:     matchLabels:
33:       app: kiwix
34:   template:
35:     metadata:
36:       labels:
37:         app: kiwix
38:     spec:
39:       securityContext:
40:         seccompProfile:
```

**chunk 3/5 (lines 41-60):**
```
41:           type: RuntimeDefault
42:       containers:
43:       - name: kiwix
44:         image: ghcr.io/kiwix/kiwix-serve
45:         securityContext:
46:           allowPrivilegeEscalation: false
47:           capabilities:
48:             drop:
49:             - ALL
50:         ports:
51:         - containerPort: 8080
52:           name: http
53:         args:
54:         - /data/wikipedia_en_all_maxi_2025-08.zim
55:         volumeMounts:
56:         - name: data
57:           mountPath: /data
58:         resources:
59:           requests:
60:             cpu: 200m
```

**chunk 4/5 (lines 61-80):**
```
61:             memory: 256Mi
62:           limits:
63:             cpu: 1000m
64:             memory: 2Gi
65:         livenessProbe:
66:           httpGet:
67:             path: /
68:             port: 8080
69:           initialDelaySeconds: 30
70:           periodSeconds: 20
71:         readinessProbe:
72:           httpGet:
73:             path: /
74:             port: 8080
75:           initialDelaySeconds: 15
76:           periodSeconds: 10
77:       volumes:
78:       - name: data
79:         persistentVolumeClaim:
80:           claimName: kiwix-data
```

**chunk 5/5 (lines 81-98):**
```
81:
82: ---
83: apiVersion: v1
84: kind: Service
85: metadata:
86:   name: kiwix
87:   namespace: kiwix
88:   labels:
89:     app: kiwix
90: spec:
91:   type: LoadBalancer
92:   loadBalancerIP: 192.168.111.101
93:   ports:
94:   - port: 80
95:     targetPort: 8080
96:     name: http
97:   selector:
98:     app: kiwix
```

---

### configs/node-main/kubernetes/kiwix-copy-job.yaml

**chunk 1/2 (lines 1-20):**
```
 1: apiVersion: batch/v1
 2: kind: Job
 3: metadata:
 4:   name: copy-zim
 5:   namespace: kiwix
 6: spec:
 7:   template:
 8:     spec:
 9:       containers:
10:       - name: copy
11:         image: busybox
12:         command:
13:         - sh
14:         - -c
15:         - |
16:           cp -v /host-zim/*.zim /data/ && echo "Copy complete!" && ls -lh /data/
17:         volumeMounts:
18:         - name: host-zim
19:           mountPath: /host-zim
20:         - name: data
```

**chunk 2/2 (lines 21-31):**
```
21:           mountPath: /data
22:       volumes:
23:       - name: host-zim
24:         hostPath:
25:           path: /home/nixos/kiwix-zim
26:           type: Directory
27:       - name: data
28:         persistentVolumeClaim:
29:           claimName: kiwix-data
30:       restartPolicy: Never
31:   backoffLimit: 2
```

---

### knowledge/hardware/server-specs/node-1/specs.md

**chunk 1/5 (lines 1-20):**
```
 1: ---
 2: title: "node-1 Hardware Specs"
 3: status: draft
 4: author: padawont
 5: date: 2026-07-14
 6: tags:
 7:   - hardware
 8:   - server-specs
 9:   - node-1
10: sources:
11:   - url: "https://www.asus.com/motherboards-components/motherboards/rog-strix/rog-strix-b550-i-gaming/"
12:     title: "ASUS ROG STRIX B550-I GAMING"
13: last_audit_date: 2026-07-14
14: related_configs:
15:   - "configs/nixos/node-1/"
16:   - "configs/kubernetes/node-1/"
17: ---
18:
19: # node-1 Hardware Specs
20:
```

**chunk 2/5 (lines 21-40):**
```
21: ## System
22:
23: | Field | Value |
24: |---|---|
25: | **Vendor** | ASUS |
26: | **Model** | ROG STRIX B550-I GAMING |
27: | **SKU** | SKU |
28: | **Firmware** | 1803 (2021-01-25) |
29: | **Chassis** | Desktop |
30: | **OS** | NixOS 26.05 (Yarara) |
31: | **Kernel** | Linux 6.18.34 |
32:
33: ## CPU
34:
35: | Field | Value |
36: |---|---|
37: | **Model** | AMD Ryzen 7 5700G with Radeon Graphics |
38: | **Cores** | 8 (16 threads) |
39: | **Sockets** | 1 |
40: | **Max Frequency** | 3.8 GHz |
```

**chunk 3/5 (lines 41-60):**
```
41: | **Min Frequency** | 1.4 GHz |
42: | **L1d Cache** | 256 KiB (8 instances) |
43: | **L1i Cache** | 256 KiB (8 instances) |
44: | **L2 Cache** | 4 MiB (8 instances) |
45: | **L3 Cache** | 16 MiB (1 instance) |
46: | **Microcode** | 0xa500012 |
47: | **Virtualization** | AMD-V |
48:
49: ## Memory
50:
51: | Field | Value |
52: |---|---|
53: | **Total** | 30 GiB |
54: | **Swap** | 8 GiB (on nvme0n1p2) |
55:
56: ## Storage
57:
58: | Device | Size | Type | Mount | Label |
59: |---|---|---|---|---|
60: | nvme0n1 | 447.1 GiB | NVMe SSD | — | — |
```

**chunk 4/5 (lines 61-80):**
```
61: | nvme0n1p1 | 512 MiB | Partition | /boot | — |
62: | nvme0n1p2 | 8 GiB | Partition | [SWAP] | — |
63: | nvme0n1p3 | 100 GiB | Partition | / | — |
64: | nvme0n1p4 | 338.6 GiB | Partition | /home | — |
65: | sda | 953.9 GiB | SATA SSD | /var/lib/longhorn | longhorn |
66: | sdb | 465.8 GiB | SATA SSD | — | — |
67: | sdc | 58.6 GiB | USB/Removable | — | NixOS installer |
68:
69: ## Network
70:
71: | Interface | MAC | IP | Purpose |
72: |---|---|---|---|
73: | `enp6s0` | `fc:34:97:65:e9:69` | 192.168.111.10/24 | Primary LAN |
74:
75: ## K3s Kubernetes
76:
77: | Component | Version |
78: |---|---|
79: | **K3s** | v1.35.5+k3s1 |
80: | **Containerd** | 2.2.3-k3s1 |
```

**chunk 5/5 (lines 81-97):**
```
81: | **Flannel** | (built-in) |
82: | **CoreDNS** | (built-in) |
83: | **Local Path Provisioner** | (built-in) |
84: | **Metrics Server** | (built-in) |
85:
86: ## Running Services (Kubernetes)
87:
88: | Namespace | Apps |
89: |---|---|
90: | `cattle-system` | Rancher, Webhook, System Upgrade Controller |
91: | `cattle-fleet-system` | Fleet Controller, GitJob, HelmOps |
92: | `cattle-capi-system` | Cluster API Controller |
93: | `cattle-turtles-system` | Rancher Turtles |
94: | `cert-manager` | cert-manager, CA Injector, Webhook |
95: | `longhorn-system` | Longhorn manager, CSI plugins, UI |
96: | `metallb-system` | MetalLB controller, FRR-K8s, Speaker |
97: | `kube-system` | CoreDNS, Local Path Provisioner, Metrics Server |
```

---

### upstream KB: knowledge-base/templates/knowledge/overview.md

**chunk 1/1 (lines 1-24):**
```
 1: ---
 2: title: ""
 3: status: draft
 4: author: ""
 5: date: YYYY-MM-DD
 6: tags: []
 7: sources:
 8:   - url: ""
 9:     title: ""
10: last_audit_date: YYYY-MM-DD
11: ---
12:
13: # {Title}
14:
15: <!--
16: Comprehensive reference on this topic.
17: Must be detailed enough for AI agents to use as a reference for actual work.
18: -->
19:
20: ## Overview
21:
22: ## Details
23:
24: ## References
```

---

### upstream KB: knowledge-base/knowledge/AGENTS.md

**chunk 1/4 (lines 1-20):**
```
 1: # Knowledge Section
 2:
 3: Knowledge contains the technical and business information required by ideas. Notes must be comprehensive enough for AI agents to use as references for actual work.
 4:
 5: ## Categorization
 6:
 7: Knowledge is grouped by category, then subcategory, then topic:
 8:
 9: ```
10: knowledge/<category>/<subcategory>/<topic>/
11: ```
12:
13: ### Top-Level Categories
14:
15: | Category | Description |
16: |---|---|
17: | `technology/` | Programming languages, frameworks, databases, tools, platforms |
18: | `business/` | Cooperative governance, finances, legal, industry domains |
19: | `design/` | UI/UX patterns, game design principles, architecture patterns |
20: | `operations/` | Deployment, CI/CD, monitoring, infrastructure |
```

**chunk 2/4 (lines 21-40):**
```
21: | `tooling/` | Developer tools, editors, build systems, project management |
22:
23: ### Examples
24:
25: ```
26: knowledge/technology/databases/postgresql/
27: knowledge/technology/game-engines/bevy/
28: knowledge/business/cooperatives/governance-models/
29: ```
30:
31: ### Anti-Patterns
32:
33: Do NOT create shallow categories like:
34: - `knowledge/php/` — too flat, no context
35: - `knowledge/waste-management/` — should be under `knowledge/business/waste-industry/`
36:
37: ## Topic Folders
38:
39: Each topic folder contains:
40:
```

**chunk 3/4 (lines 41-60):**
```
41: | File | Required | Purpose |
42: |---|---|---|
43: | `README.md` | Yes | Basic description and index |
44: | Atomic `.md` files | Yes (2+) | Multiple focused notes, each covering one concept |
45: | `overview.md` | No | Optional summary — only if a single overview is explicitly requested |
46:
47: **Atomic notes rule:** Break content into focused files rather than one comprehensive `overview.md`. Each atomic note covers exactly one concept. Use the README.md as an index linking to all notes in the folder.
48:
49: ### Example
50:
51: ```
52: knowledge/design/documentation/diataxis/
53: +-- README.md              # Index linking to each atomic note
54: +-- tutorials.md           # Tutorial quadrant
55: +-- how-to-guides.md       # How-to guide quadrant
56: +-- reference.md           # Reference quadrant
57: +-- explanation.md         # Explanation quadrant
58: +-- quality-model.md       # Functional vs deep quality
59: ```
60:
```

**chunk 4/4 (lines 61-78):**
```
61: ### When to Split
62:
63: Split when the topic has:
64: - Multiple distinct subtopics that can stand alone (each gets its own file)
65: - Concepts at different levels of detail (one file per concept)
66: - Independent reference value (reader should find one without reading all)
67:
68: Do NOT split when the topic is genuinely a single concept — one focused file is fine.
69:
70: ## Frontmatter Requirements
71:
72: All atomic `.md` files (including `overview.md` if present) must include in frontmatter:
73: - `sources` — URLs of where this note is based on
74: - `last_audit_date` — date of the last accuracy review
75:
76: ## Status Lifecycle
77:
78: `draft` → `exploring` → `accepted` → `completed` / `superseded`
```

---

## Online Documentation

### https://github.com/kiwix/kiwix-tools

**chunk 1/5 (README.md lines 1-40):**
```
Kiwix tools — collection of command line tools: kiwix-manage, kiwix-search, kiwix-serve.
License: GPLv3+
Latest release: 3.8.2 (Mar 2, 2026)
Stars: 892, Forks: 134, Commits: 1,330
Docker images: ghcr.io/kiwix/kiwix-tools and ghcr.io/kiwix/kiwix-serve
```

**chunk 2/5 (lines 41-80):**
```
Dependencies: libkiwix, libzim. Build system: Meson + Ninja.
Compilation: meson . build && ninja -C build
Installation: ninja -C build install (may need sudo)
Static linkage: -Dstatic-linkage=true
```

**chunk 3/5 (lines 81-120):**
```
Docker images available on GHCR:
- ghcr.io/kiwix/kiwix-tools (all tools)
- ghcr.io/kiwix/kiwix-serve (dedicated server image)
Multi-arch: amd64, arm64, arm32v7
Topics: http, library, offline, daemon, kiwix, zim
```

---

### https://kiwix-tools.readthedocs.io/en/stable/kiwix-serve.html

**chunk 1/8 (lines 1-60):**
```
kiwix-serve — HTTP daemon serving ZIM files.
Usage:
  kiwix-serve --library [OPTIONS] LIBRARY_FILE_PATH
  kiwix-serve [OPTIONS] ZIM_FILE_PATH ...

Options:
  --library           Use XML library file instead of direct ZIM paths
  --catalogOnly       Serve only welcome page and OPDS catalog
  --contentServerURL  URL of a separate content-serving instance
  -i ADDR, --address  Bind address (default: all interfaces)
  -p PORT, --port     TCP port (default: 80, 8080 in Docker)
  -r ROOT, --urlRootLocation  URL path prefix
  -d, --daemon        Detach from main process
  -a PID, --attachToProcess  Exit when PID stops
  -M, --monitorLibrary  Reload library XML on changes
  -m, --nolibrarybutton  Disable library home button
  -n, --nosearchbar   Disable searchbox in viewer
  -b, --blockexternal  Block external resource navigation
  -t N, --threads     Number of threads (default: 4)
  -s N, --searchLimit Max ZIM files in fulltext search
  -z, --nodatealiases  Remove date from URL aliases
  -c PATH, --customIndex  Custom welcome page HTML
  -L N, --ipConnectionLimit  Max concurrent connections per IP
  -v, --verbose       Debug log to STDOUT
```

**chunk 2/8 (lines 61-120):**
```
HTTP API — endpoints relative to http://ADDR:PORT/ROOT:

/ (welcome page) — private. Library page with book listing/filtering.
/catalog/v2 (OPDS API) — public. Based on OPDS Catalog v1.2.
  /catalog/v2/root.xml — OPDS Catalog Root
  /catalog/v2/searchdescription.xml — OpenSearch description
  /catalog/v2/categories — ZIM file categories as navigation feed
  /catalog/v2/entries — full/filtered ZIM list (paginated)
    Supports: lang, category, tag, notag, maxsize, q, name filters
    Pagination: start, count params (default 10 per page)
  /catalog/v2/entry/ZIMID — full info by UUID
  /catalog/v2/illustration/ZIMID?size=N — illustration by size
  /catalog/v2/languages — language list as navigation feed
  /catalog/v2/partial_entries — partial entries (lightweight)
```

**chunk 3/8 (lines 121-180):**
```
/catalog (Legacy OPDS) — deprecated, preserved for backward compat.
  /catalog/root.xml — full library OPDS catalog
  /catalog/searchdescription.xml — OpenSearch description
  /catalog/search — filtered ZIM search

/catch/external?source=URL — private. Warning page for external links.
/content — private. ZIM file content serving.
  /content/ZIMNAME/PATH/IN/ZIMFILE — content by ZIM name and path
  /content/ZIMNAME — redirects to main page of ZIM file
/random?content=ZIMNAME — random article redirect
```

**chunk 4/8 (lines 181-240):**
```
/raw — public. Raw ZIM file data access.
  /raw/ZIMNAME/content/PATH/IN/ZIMFILE — raw content (no server processing)
  /raw/ZIMNAME/meta/METADATAID — metadata item

/search — public. Full text search across ZIM files.
  Supports: content, books.id, books.name, books.filter.{criteria}
  Query params: pattern, latitude, longitude, distance
  Pagination: pageLength (max 140), start
  Format: html (default) or xml

  /search/searchdescription.xml — OpenSearch description

/suggest — private. Auto-complete suggestions for page titles.
  Params: content (ZIM name), term, count (default 10), start
  Uses title index; case-insensitive if index exists
```

**chunk 5/8 (lines 241-300):**
```
/viewer — private. ZIM file viewer via URL hash: /viewer#ZIMNAME/PATH
/viewer_settings.js — private. JS settings for viewer

Glossary:
  Book name — name from ZIM metadata or library XML
  ZIM filename — filesystem name
  ZIM name — derived from filename (lowercase, no diacritics, spaces→_, +→plus)
  ZIM title — display title (text with whitespace)
  ZIM UUID — unique identifier embedded at creation time
```

---

### https://hub.kiwix.org/downloads/ (Kiwix Hub Downloads page)

**chunk 1/1 (lines 1-20):**
```
Kiwix Hub - Downloads page.
Links:
  - ZIM files: https://browse.library.kiwix.org/
  - Kiwix readers: https://get.kiwix.org/solutions/applications/kiwix-reader/
  - Kiwix Server: https://get.kiwix.org/solutions/applications/kiwix-server/
  - Extended releases: https://get.kiwix.org/applications/download-options/
  - All releases (folder): https://mirror.download.kiwix.org/release/
  - Nightly builds: https://mirror.download.kiwix.org/nightly/
  - openZIM releases: https://download.openzim.org/release/
  - openZIM nightly: https://download.openzim.org/nightly/
  - Archives: https://archive.download.kiwix.org/
  - Technical details: https://github.com/kiwix/operations/wiki/Downloads
```

---

### https://hub.docker.com/r/kiwix/kiwix-serve

[FETCH FAILED] — HTTP 404 returned. The official kiwix-serve Docker image is hosted on GHCR (ghcr.io/kiwix/kiwix-serve), not Docker Hub. This was already confirmed by the kiwix-tools GitHub README which links to GHCR.

### https://github.com/orgs/kiwix/packages/container/kiwix-serve

[FETCH FAILED] — HTTP 500 returned from GitHub packages page. The image can still be pulled: `docker pull ghcr.io/kiwix/kiwix-serve`.

---

## Definition of Done

- [ ] Deploy `kiwix.yaml` to the K3s cluster
- [ ] Deploy `kiwix-copy-job.yaml` to copy ZIM files from host path to Longhorn PVC
- [ ] Verify the kiwix-serve pod is running (`kubectl -n kiwix get pods`)
- [ ] Verify the Service gets LoadBalancer IP 192.168.111.101
- [ ] Verify HTTP 200 response at http://192.168.111.101/
- [ ] Verify Wikipedia content loads in browser
- [ ] Verify ZIM file is on the Longhorn PVC (approximate size ~115 GB)
- [ ] Verify resource limits (CPU 1000m, memory 2Gi) are not exceeded
- [ ] Verify liveness/readiness probes are green (`kubectl -n kiwix describe pod`)
- [ ] Update knowledge notes from `draft` → `completed` status
- [ ] Create a changelog entry for the deployment
- [ ] Verify ZIM format compatibility (current kiwix-serve 3.8.2)

## PR Acceptance Criteria

1. All manifests in `configs/node-main/kubernetes/` are syntactically valid YAML
2. PVC `kiwix-data` requests exactly 150Gi with `longhorn` storage class
3. Deployment uses `ghcr.io/kiwix/kiwix-serve` (no `:latest` tag; use explicit version)
4. Security context drops all capabilities, disallows privilege escalation
5. Service type is `LoadBalancer` with `loadBalancerIP: 192.168.111.101`
6. Service maps port 80 → targetPort 8080
7. Copy job uses `busybox` image, mounts host path `/home/nixos/kiwix-zim`
8. Copy job has `restartPolicy: Never` and `backoffLimit: 2`
9. Knowledge documents have `status: completed` with correct `last_audit_date`
10. Changelog entry follows `changelog/AGENTS.md` format
11. All cross-links between knowledge/, configs/, changelog/ are valid
12. No hardcoded secrets or exposed credentials
