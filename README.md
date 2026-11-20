# Lab 4: Advanced Deployment Strategies & Enterprise DevOps

**Name:** Amit · **Roll No.:** 2301010471

A small Flask app is used to demonstrate CI/CD test gates (Jenkins), blue-green and canary deployments, GitOps
(Argo CD), secret management (HashiCorp Vault) and disaster recovery on Minikube.

## Structure

```
app/                     Flask app (version, color, /health, /secret-check, /notes backed by Redis)
tests/                   unit tests (in-process) and integration tests (against the running container)
Dockerfile               application image
Jenkinsfile              pipeline: Unit Tests -> Build -> Integration Tests -> Vault secrets -> Deploy -> Smoke Test
jenkins/                 Jenkins image + init script (admin user, Vault credential, pipeline job)
k8s/app/                 app deployed by Jenkins (password from a Kubernetes Secret)
k8s/blue-green/          blue + green Deployments and the switchable Service
k8s/canary/              stable (4 pods) + canary (1 pod) behind one Service
k8s/dr/                  Redis with a PersistentVolumeClaim + notes app (2 replicas)
k8s/vault/               HashiCorp Vault (dev mode)
gitops/                  Argo CD Application + the manifests it keeps in sync
scripts/                 blue-green switch, traffic generator, canary analysis, backup and restore
```

## Quick start

```bash
minikube start -p lab4 --driver=docker --container-runtime=docker --memory=4096
eval $(minikube -p lab4 docker-env)
docker build -t lab4-app:1.0 . && docker build --build-arg APP_VERSION=2.0 -t lab4-app:2.0 .
```

| Experiment | Main commands |
|---|---|
| CI/CD test gates | `docker build -t lab4-jenkins jenkins/` then run the `lab4-pipeline` job |
| Blue-green | `kubectl -n lab4-bg apply -f k8s/blue-green/` · `scripts/blue-green-switch.sh green` |
| Canary | `kubectl -n lab4-canary apply -f k8s/canary/` · `scripts/canary-analyze.sh` |
| GitOps | `kubectl apply -f gitops/application.yaml` - then change `gitops/manifests/` and push |
| Secrets | `vault kv put secret/lab4/app db_password=...` - Jenkins reads it with a read-only token |
| Disaster recovery | `scripts/backup.sh lab4-dr` · `scripts/restore.sh backups/<time> lab4-dr` |

No passwords or tokens are stored in this repository.
