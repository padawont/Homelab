# Validation: configs/node-main/kubernetes/kiwix.yaml

## DoD Compliance
- [PASS] Namespace kiwix defined
- [PASS] PVC: kiwix-data, longhorn, ReadWriteOnce, 200Gi
- [PASS] Deployment: image ghcr.io/kiwix/kiwix-serve:3.8.2, args correct
- [PASS] Security: seccomp RuntimeDefault, noPrivilegeEscalation, drop ALL
- [PASS] Port 8080 named http
- [PASS] Liveness/readiness probes on GET / port 8080
- [PASS] Resources: requests cpu 200m mem 256Mi, limits cpu 1000m mem 2Gi
- [PASS] Service: LoadBalancer, IP 192.168.111.101, port 80→8080
- [PASS] Copy Job: busybox, hostPath /home/nixos/kiwix-zim, PVC kiwix-data
- [PASS] restartPolicy Never, backoffLimit 2
- [PASS] All YAML valid
- [PASS] Internal consistency (selector labels, claimName all match)
Score: 12/12

## PR Criteria
- [PASS] YAML syntax valid
- [PASS] All inline references point to real files
- [PASS] No hardcoded secrets
- [PASS] PVC size adequate for 119GB ZIM file (200Gi)
Score: 4/4

## Syntax Check
- [PASS] YAML: 4 valid documents (Namespace, PVC, Deployment, Service)

## Reference Integrity
- [PASS] .research/kiwix-research.md
- [PASS] knowledge/kubernetes/kiwix/kiwix-serve-config.md

# Validation: configs/node-main/kubernetes/kiwix-copy-job.yaml

## DoD Compliance
- [PASS] Namespace kiwix (matches kiwix.yaml)
- [PASS] PVC claimName kiwix-data (matches kiwix.yaml)
- [PASS] busybox image
- [PASS] hostPath /home/nixos/kiwix-zim
- [PASS] restartPolicy Never
- [PASS] backoffLimit 2
Score: 6/6

## PR Criteria
- [PASS] YAML syntax valid
- [PASS] Inline references point to real files
- [PASS] No hardcoded secrets
Score: 3/3

## Syntax Check
- [PASS] YAML: 1 valid document (Job)

## Reference Integrity
- [PASS] .research/kiwix-research.md
