# Setup Dagger

## Prerequisites

- Docker installed and running on the system
- DevBox environment configured (`devbox.json` updated with `dagger@latest`)
- (Optional) Forgejo deployed for CI integration (see `deployment/procedures/deploy-forgejo.md`)

## Steps

### 1. Install Dagger CLI via devbox

```bash
devbox add dagger@latest
```

If nixpkgs provides an outdated version, install directly:

```bash
curl -fsSL https://dl.dagger.io/dagger/install.sh | BIN_DIR=$HOME/.local/bin sh
```

### 2. Verify installation

```bash
dagger version
```

Expected output: `dagger v0.21.x (registry.dagger.io/engine:v0.21.x) linux/amd64`

### 3. Start Dagger Engine

The engine auto-provisions on first use:

```bash
dagger run echo "engine started"
```

Verify the engine container is running:

```bash
docker ps --filter='name=^dagger-engine-'
```

### 4. Test Python SDK

```bash
pip install dagger-io
python -c "import dagger; print(f'Python SDK OK: {dagger.__version__}')"
```

### 5. Run a simple pipeline

Create a test module directory:

```bash
mkdir -p /tmp/dagger-test && cd /tmp/dagger-test
dagger init --sdk=python --name=hello
```

Write a simple function in `src/hello/__init__.py`:

```python
import anyio
from dagger import function, object_type, dag


@object_type
class Hello:
    @function
    async def greet(self) -> str:
        return await (
            dag.container()
            .from_("alpine:latest")
            .with_exec(["echo", "hello dagger"])
            .stdout()
        )
```

Run it:

```bash
dagger call greet
```

### 6. (Optional) Deploy persistent engine to node-1

```bash
kubectl apply -f configs-and-adr/node-main/kubernetes/dagger-engine.yaml
```

This creates a DaemonSet running the Dagger Engine on node-1 with a Longhorn-backed cache volume.

### 7. Create Forgejo Actions workflow

Create `.forgejo/workflows/ci.yml` in your repository:

```yaml
name: CI
on: [push, pull_request]
jobs:
  dagger:
    runs-on: docker
    steps:
      - uses: actions/checkout@v4
      - run: dagger call test --source=.
```

### 8. Test full flow

```bash
git add .forgejo/workflows/ci.yml
git commit -m "ci: add Dagger pipeline trigger"
git push <forgejo-remote> main
```

Verify the Forgejo Actions run triggers and executes `dagger call`.

## Verification

```bash
dagger call --help
dagger version
python -c "import dagger; print(dagger.__version__)"
```

## Rollback

```bash
# Remove from devbox
devbox remove dagger

# Remove CLI binary (if installed directly)
sudo rm /usr/local/bin/dagger

# Stop and remove engine
docker rm --force --volumes "$(docker ps --quiet --filter='name=^dagger-engine-')"

# Remove persistent engine from cluster
kubectl delete -f configs-and-adr/node-main/kubernetes/dagger-engine.yaml

# Clean cache directories
rm -rf ~/.cache/dagger ~/.config/dagger
```
