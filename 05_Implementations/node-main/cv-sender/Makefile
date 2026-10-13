# cv sender worker — build, import, and deploy helpers (ADR-612, issue #614).

IMAGE     ?= cv-sender:0.1
NAMESPACE ?= cv-sender
KUBECTL   ?= kubectl

# Local run mirrors the Deployment mounts (configs/deployment.yaml):
#   data/        -> /app/data            (state.db, preview.csv)
#   data/cv/     -> /app/config/cv       (CV attachment, read-only)
#   configs/config.yaml -> /app/config/config.yaml (read-only)
# Secrets are never mounted into the image; `pilot` pulls them from .env at runtime.
RUN_ARGS = --rm \
	-v "$(CURDIR)/data:/app/data" \
	-v "$(CURDIR)/data/cv:/app/config/cv:ro" \
	-v "$(CURDIR)/configs/config.yaml:/app/config/config.yaml:ro"

.PHONY: build import dry-run pilot deploy logs clean

# Build the worker image locally.
build:
	docker build -t $(IMAGE) .

# Import the image into the k3s containerd store on the node.
import:
	docker save $(IMAGE) | sudo k3s ctr images import -

# Smoke-test the worker end to end without sending any mail (no secret required).
dry-run:
	docker run $(RUN_ARGS) $(IMAGE) --dry-run

# Bounded pilot rollout (rate-limited, pilot_count recipients) before full rollout.
pilot:
	docker run $(RUN_ARGS) --env-file .env $(IMAGE) --pilot

# Apply in-cluster manifests (Deployment, PVC, ConfigMap, Secret).
deploy:
	$(KUBECTL) apply -f configs/

# Tail worker logs from the deployment.
logs:
	$(KUBECTL) -n $(NAMESPACE) logs -f deploy/cv-sender

# Remove local build artefacts.
clean:
	-docker image rm -f $(IMAGE)
