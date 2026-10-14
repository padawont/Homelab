# cv sender worker — build, import, and deploy helpers (ADR-612, epic #611).

IMAGE     ?= cv-sender:0.1
NAMESPACE ?= cv-sender
KUBECTL   ?= kubectl
CONFIG    ?= configs/config.yaml
ENV_FILE  ?= .env
ENV_ARG   = $(if $(wildcard $(ENV_FILE)),--env-file $(ENV_FILE),)

# Local run mirrors the Deployment mounts (configs/deployment.yaml):
#   data/        -> /app/data            (state.db, preview.csv)
#   data/cv/     -> /app/config/cv       (CV attachment, read-only)
#   configs/config.yaml -> /app/config/config.yaml (read-only)
# Secrets are never mounted into the image; `pilot` pulls them from .env at runtime.
RUN_ARGS = --rm \
	-v "$(CURDIR)/data:/app/data" \
	-v "$(CURDIR)/data/cv:/app/config/cv:ro" \
	-v "$(CURDIR)/$(CONFIG):/app/config/config.yaml:ro"

.PHONY: build import dry-run pilot test-flows deploy logs clean

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
# Requires .env (see .env.example) to define all three variables:
# GMAIL_APP_PASSWORD, CV_SENDER_SIGNATURE_NAME and CV_SENDER_SIGNATURE_PHONE.
pilot:
	docker run $(RUN_ARGS) --env-file .env $(IMAGE) --pilot

# Run the in-image flow tests (Playwright/Chromium only exists in the image).
# `--entrypoint python` overrides the image ENTRYPOINT (`python -m src.main
# worker`) so it is not prepended to the unittest command below.
test-flows:
	docker run $(RUN_ARGS) $(ENV_ARG) \
		-v "$(CURDIR)/tests:/app/tests" \
		--entrypoint python \
		$(IMAGE) -m unittest discover -s tests -v

# Apply in-cluster manifests in dependency order (namespace → Secret → ConfigMap → PVC → Deployment).
deploy:
	$(KUBECTL) apply -f configs/namespace.yaml
	$(KUBECTL) apply -f configs/secret.yaml
	$(KUBECTL) apply -f configs/configmap.yaml
	$(KUBECTL) apply -f configs/pvc.yaml
	$(KUBECTL) apply -f configs/deployment.yaml

# Tail worker logs from the deployment.
logs:
	$(KUBECTL) -n $(NAMESPACE) logs -f deploy/cv-sender

# Remove local build artefacts.
clean:
	-docker image rm -f $(IMAGE)
