# Harvester Manifests

Helm values and Kustomize overlays for Rancher Harvester integration.

## Contents

| File | Purpose |
|------|---------|
| `rancher-integration-values.yaml` | Helm values for Harvester CSI driver and cloud provider integration with Rancher |

## Related Configs

Raw Harvester configuration (install config YAML) lives in `configs-and-adr/node-main/vm/harvester-config.yaml`. The Rancher integration procedure is documented in `deployment/procedures/deploy-harvester.md`.

## Usage

Deploy the CSI driver and cloud provider on guest K3s clusters provisioned via the Harvester node driver:

```bash
# Install Harvester CSI Driver via Rancher Marketplace
# Chart: harvester-csi-driver (from Rancher charts)
# Values: custom values from rancher-integration-values.yaml

# Or manual install:
helm repo add harvester https://charts.harvesterhci.io
helm install harvester-csi-driver harvester/harvester-csi-driver \
  -n harvester-system \
  -f deployment/manifests/harvester/rancher-integration-values.yaml
```
