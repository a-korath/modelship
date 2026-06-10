# Handoff Document — Week 4 Complete, Week 5 Next

## Status

Weeks 1–4 are fully complete. Smoke test passed. Ready for Week 5: Auth + Security.

## Last Smoke Test Results

```
GET  /health  → {"status":"ok","model_loaded":true}
POST /predict → POSITIVE 0.9999  ("I love this!")
POST /predict → NEGATIVE 0.9996  ("This is terrible.")
GET  /model/info → model_loaded: true, loaded_at: 2026-06-01T00:42:34
```

## What Was Built (Weeks 1–4)

| Week | What's done |
|------|-------------|
| 1 | FastAPI app, /predict, /health, /model/info, Pydantic validation, Dockerfile |
| 2 | **NOT DONE** — .github/workflows/ is empty. Planned after Week 5. |
| 3 | MLflow tracking server, DistilBERT registered with alias "Production" |
| 4 | K8s manifests (Deployment, Service, Ingress, ConfigMap, HPA), running on minikube |
| 5 | Next up |

## Key Files Changed During Week 3–4 Debug

- `docker/Dockerfile.mlflow` — `mlflow-skinny[db]` → `mlflow[server]==3.12.0`; removed dead CMD
- `k8s/mlflow-deployment.yaml` — added `--artifacts-destination file:///mlflow/artifacts`; memory limit 1500Mi
- `k8s/deployment.yaml` — startup probe failureThreshold 6→60 (10 min budget); memory limit 1Gi→2Gi; cpu limit 2
- `src/api/models/ml_model.py` — switched from deprecated stages API to alias API (`models:/name@Production` + `get_model_version_by_alias`)
- `src/api/routes/model_info.py` — imports `ml_model` module, reads `ml_model.MODEL_VERSION` at request time (not import time)
- `src/api/routes/predict.py` — same fix as model_info.py
- `mlflow/mlflow.db` — artifact URIs rewritten from local POSIX paths to `mlflow-artifacts:/` scheme

## The Big Bug: MLflow Artifact Registration (full explanation)

Four separate problems were stacked on top of each other. Each one alone would cause failure.

**Problem 1 — MLflow server CrashLoopBackOff**
`mlflow-skinny[db]` is a client-only package. It's missing gunicorn, flask-cors, and other server deps. The server entry point doesn't exist in it. Fix: use `mlflow[server]` which is the canonical server package.

**Problem 2 — Getting 268MB model files into K8s**
Three approaches failed:
- `mlflow.log_artifacts` over `kubectl port-forward` → connection drops after ~120s (port-forward is a debug tunnel, not a data pipeline)
- `kubectl cp` → runs `tar` inside the receiving pod, hits 1Gi memory limit, exit code 137 (OOMKill — kernel SIGKILL, no Python stack trace)
- `minikube cp` / SSH pipe → hangs indefinitely or prints binary garbage

What worked: minikube stores PVC data in the VM filesystem at `/tmp/hostpath-provisioner/default/mlflow-pvc/`. Wrote files directly into the VM using `docker exec -i minikube bash -c 'cat > /path'`, bypassing the pod entirely.

**Problem 3 — Wrong artifact addresses in the database**
The model was registered via docker-compose with `MLFLOW_TRACKING_URI=sqlite:////mlflow/mlflow.db`. MLflow stored artifact locations as local POSIX paths (`/mlflow/artifacts/0/<run_id>/...`). Inside the K8s API pod, that path doesn't exist — the PVC isn't mounted there. Fix: rewrote `source` and `storage_location` columns in SQLite to use `mlflow-artifacts:/0/<run_id>/artifacts/<name>` so MLflow uses its HTTP proxy instead of direct filesystem access.

**Problem 4 — MLflow proxy serving from wrong folder**
`--default-artifact-root mlflow-artifacts:/` alone isn't enough. Without `--artifacts-destination`, the proxy defaults to `./mlartifacts` relative to cwd `/` — an empty directory. The PVC is at `/mlflow`. Fix: add `--artifacts-destination file:///mlflow/artifacts` to the server command.

**Bonus — "Production" stage vs alias mismatch**
MLflow has two unrelated features both called "Production": stages (old API) and aliases (new API). The model was registered with an alias, but the code used `get_latest_versions(stages=["Production"])` which returned empty. Fix: switch to `models:/name@Production` and `get_model_version_by_alias`.

**Bonus — MODEL_VERSION import snapshot bug**
`from src.api.models.ml_model import MODEL_VERSION` grabs the value at import time ("Production"). When `load_model()` later updates the variable to "6", the routes never see the update. Fix: import the module and read `ml_model.MODEL_VERSION` at request time.

## Interview Prep Bullets From This Debug

- Exit code 137 = SIGKILL from kernel OOM killer, not Python. No stack trace. Confirmed via `kubectl describe pod` showing `Reason: OOMKilled`
- `kubectl port-forward` is a debug tunnel over HTTP/2 SPDY — not designed for bulk data. Use a Job or sidecar for large transfers
- K8s PVCs with hostPath provisioner store data at `/tmp/hostpath-provisioner/<ns>/<pvc>/` on the minikube VM — accessible via `minikube ssh` or `docker exec minikube`
- MLflow has two artifact retrieval paths: direct filesystem (local URI) vs HTTP proxy (`mlflow-artifacts:/`). The registry remembers which was active at registration time. Mixing them silently breaks loading
- Python `from module import VAR` is a snapshot. If the original module later changes `VAR`, your copy stays stale. Use `module.VAR` to always read the current value

## Week 5 Scope: Auth + Security

Files to create/fill in:
- `src/api/middleware/auth.py` — JWT validation + API key management
- `src/api/middleware/rate_limit.py` — token bucket rate limiter (100 req/min per key)

Features to build:
- JWT auth middleware (validate token on every request)
- API key endpoints: create, revoke, list
- Rate limiting: 100 req/min per key using token bucket algorithm
- Role-based access: admin vs. user keys
- Input sanitization
- Security headers (CORS, HSTS)
- TLS via Let's Encrypt or cloud-provided

Checkpoint: 401 for unauthenticated requests, 429 for rate-limited, all HTTPS

## Teaching Context

**Who:** 2027 new grad targeting ML Platform Engineer / MLOps roles. ModelShip is a depth portfolio project — the goal is genuine understanding for job readiness, not just working code.

**Role:** You are an advisor, not an assistant. You do not do things for the user — you help them figure out how to do things themselves. The distinction matters: an assistant produces output, an advisor builds capability.

**Teaching style — Explain + implement together.**
- For each new concept, decision, or feature: generate a section in this order:
  1. **The logic** — how it works mechanically
  2. **Why this decision** — the tradeoff or constraint that drove the choice
  3. **What it does** — the observable effect or contract from the caller's perspective
- Then provide the implementation. Explanation and code go together — understanding the why AND seeing the how.
- After the explanation + code, ask one targeted question to confirm understanding before moving on.
- Cross-concept connecting questions work well ("how does this relate to X you built earlier?")
- Grill sessions and interview simulations land well — use them often.

**Pacing — one step at a time.**
- Propose the next single step, wait for confirmation before proceeding.
- Never bulk-scaffold files or directories in one shot — user wants to understand each piece as it's built.

**Interview coaching notes:**
- User hesitates before connecting pieces they already know — push them to complete the answer in one breath, don't let them trail off.
- Rollback story: change `@Production` alias in MLflow → rolling update picks it up — this is a strong interview answer, coach it.
- When asked "why did you build this?" — coach to lead with the hot-reload consistency problem, not job market motivation.

## To Resume

```bash
minikube start
kubectl get pods  # wait for all 3 to be Running
kubectl port-forward svc/modelship-service 8000:8000
curl http://127.0.0.1:8000/health  # should show model_loaded: true
```
