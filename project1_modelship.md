# Project: ModelShip — ML Deployment Platform

## Current Status (as of 2026-06-09)

**Completed:** Weeks 1, 3, 4 (API + Docker, MLflow registry, K8s deployment on minikube)
**Next up:** Week 5 — Auth + Security
**Deferred:** Week 2 (CI/CD pipeline) — pushed after Week 5 once auth boundary exists to test against
**Not yet done:** Public cloud deployment (still local minikube), CI/CD, monitoring, load testing, polish

**Quick reality check on the doc:**
- Tech stack lists "K3s locally" — actual setup is **minikube** with the hostpath-provisioner storage class
- Week 4 checkpoint says "API live at public URL" — this hasn't happened; API is reachable via `minikube tunnel`/port-forward only
- Week 2's deferral means the current dev loop is `make build && kubectl rollout restart` — no automated image push, no green-pipeline gate

---

## What this project is

ModelShip is an end-to-end ML deployment platform that takes a trained machine learning model and ships it to production through an automated, secure, monitored pipeline. It's a mini-SageMaker built from scratch. The goal is to demonstrate deep expertise in MLOps, AI infrastructure, model lifecycle management, and production engineering — targeting ML Platform Engineer, MLOps Engineer, and AI Infrastructure roles for the 2027 new grad market.

This is the **depth** project in a T-shaped portfolio strategy. It goes deep on ML infrastructure while demonstrating security, observability, and production thinking. The model itself is intentionally boring (off-the-shelf HuggingFace sentiment classifier) — every joule of effort goes into the platform around it.

## Tech stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| Language | Python 3.11+ | Primary language for ML ecosystem, FastAPI, and tooling |
| Model serving | FastAPI | Async, auto-generated OpenAPI docs, Pydantic validation, lighter than Flask for API-first work |
| Model tracking | MLflow (`mlflow[server]`, NOT `mlflow-skinny`) | Industry standard for experiment tracking and model registry. Self-hosted. |
| Containerization | Docker (multi-stage builds) | Non-negotiable for infra roles. Multi-stage builds demonstrate optimization awareness. |
| Local orchestration | **minikube** (hostpath-provisioner) | Single-VM K8s, runs the same manifests EKS/GKE would. Used K3s in original plan; switched to minikube for better Docker desktop integration. |
| Production orchestration | EKS or GKE free tier (planned) | Managed K8s for public deployment |
| CI/CD | GitHub Actions (deferred to post–Week 5) | Free for public repos, YAML-based, visible to interviewers |
| Monitoring | Prometheus + Grafana | Industry standard. Prometheus scrapes metrics, Grafana visualizes. |
| Load testing | Locust | Python-native, clean HTML reports for README |
| Auth/Security | Custom middleware (JWT + API keys + token-bucket rate limiting) | Building it from scratch IS the point — demonstrates security engineering depth |
| Cloud | AWS free tier (EC2 + ECR) — fallback GCP | AWS has more resume recognition |
| Model | Pre-trained HuggingFace DistilBERT (sentiment) | Model complexity is irrelevant — all energy goes to infrastructure |
| Linting | Ruff | Fast Python linter, replaces flake8 + black + isort |
| Testing | Pytest | Standard Python testing framework |
| Build tools | Makefile + `pyproject.toml` | `make build/test/run/push/deploy` |

## Architecture

```
Client Request (REST/gRPC)
         │
         ▼
┌──────────────────────────────────┐
│  API Gateway / Auth Layer        │
│  ├─ JWT token validation         │
│  ├─ API key management           │
│  ├─ Rate limiting (token bucket) │
│  ├─ TLS termination              │
│  ├─ Request logging              │
│  └─ Input sanitization           │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│  Model Serving (FastAPI)         │
│  ├─ /predict — inference         │
│  ├─ /health — liveness check     │
│  ├─ /metrics — Prometheus scrape │
│  ├─ /model/info — version info   │
│  ├─ /docs — auto OpenAPI docs    │
│  ├─ Input preprocessing          │
│  └─ Response formatting          │
└───────┬──────────────┬───────────┘
        │              │
        ▼              ▼
┌─────────────┐  ┌─────────────────────┐
│ MLflow      │  │ Prometheus          │
│ Registry    │  │ Metrics             │
│ ├─ Versions │  │ ├─ Latency (p50/95) │
│ ├─ Metadata │  │ ├─ Throughput (RPS) │
│ ├─ Artifacts│  │ ├─ Error rates      │
│ └─ Aliases  │  │ ├─ Model drift      │
│   (@Prod,   │  │ ├─ Prediction dist  │
│    @Staging)│  │ └─ Confidence hist  │
└─────────────┘  └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Grafana Dashboards  │
                 │ ├─ API performance  │
                 │ ├─ Model health     │
                 │ ├─ Cost estimates   │
                 │ └─ Alert rules      │
                 └─────────────────────┘
```

**CI/CD Pipeline (GitHub Actions — Week 2, deferred):**
```
git push → trigger →
  1. Lint (ruff)
  2. Test (pytest)
  3. Build Docker image (multi-stage)
  4. Push to container registry (tag = git SHA)
  5. Deploy to K8s (rolling update via kubectl set image)
  6. Smoke test against live endpoint
  7. Annotate Grafana deployment marker
```

## Repo structure

```
modelship/
├── src/
│   ├── api/
│   │   ├── main.py              # FastAPI app entry
│   │   ├── routes/
│   │   │   ├── predict.py
│   │   │   ├── health.py
│   │   │   └── model_info.py
│   │   ├── middleware/
│   │   │   ├── auth.py          # JWT + API key validation
│   │   │   ├── rate_limit.py    # Token bucket rate limiter
│   │   │   └── logging.py
│   │   ├── models/
│   │   │   ├── schemas.py       # Pydantic request/response models
│   │   │   └── ml_model.py      # Model loading from MLflow
│   │   └── metrics/
│   │       └── prometheus.py    # Custom metric definitions
│   └── scripts/
│       ├── promote_model.py     # MLflow alias swap (@Staging → @Production)
│       └── load_test.py         # Locust test definitions
├── tests/
│   ├── test_predict.py
│   ├── test_auth.py
│   ├── test_rate_limit.py
│   └── test_model_loading.py
├── docker/
│   ├── Dockerfile               # Multi-stage production build
│   └── Dockerfile.dev           # Development with hot reload
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   ├── pvc.yaml                 # PVC for MLflow artifact store
│   └── hpa.yaml                 # Horizontal pod autoscaler
├── mlflow/
│   └── Dockerfile               # mlflow[server] image (NOT mlflow-skinny)
├── monitoring/
│   ├── prometheus.yml
│   ├── grafana/dashboards/
│   │   ├── api-performance.json
│   │   └── model-health.json
│   └── alerts/rules.yml
├── .github/workflows/
│   ├── ci.yml                   # Lint + test + build
│   └── deploy.yml               # Deploy to cloud
├── docker-compose.yml           # Full local dev environment
├── Makefile
├── pyproject.toml
├── README.md
└── docs/
    ├── ARCHITECTURE.md
    ├── DESIGN_DECISIONS.md
    ├── SCALE_CONSIDERATIONS.md
    └── LOAD_TEST_REPORT.md
```

## Timeline — 8 weeks of work

Status legend: ✅ done · 🟡 in progress · ⏸ deferred · ⬜ not started

### Week 1: API foundation + Docker ✅
- Repo scaffolded
- DistilBERT sentiment model running locally
- FastAPI app with `/predict`, `/health`, `/docs`
- Pydantic input validation
- Multi-stage Dockerfile
- `docker-compose.yml` for local dev
- 5+ unit tests
- **Checkpoint met:** `docker-compose up` → `curl localhost:8000/predict` returns a real prediction

### Week 2: CI/CD pipeline ⏸ (deferred — resuming Wed 2026-06-11)
- GitHub Actions: `ruff` → `pytest` → docker build → push to registry
- Image tagging with git SHA
- Makefile: `make build/test/run/push`
- Branch protection (CI must pass)
- **Deferral reason:** auth boundary (Week 5) needs to exist before the deploy job can run a meaningful smoke test, and the manual `make build && kubectl rollout restart` loop is fast enough during single-developer iteration.
- **Checkpoint when resumed:** Every push triggers green pipeline and ships a SHA-tagged image to the registry.

### Week 3: MLflow model registry ✅
- MLflow tracking server in docker-compose (using `mlflow[server]`, with `--serve-artifacts --artifacts-destination file:///mlflow/artifacts`)
- Model registered with version metadata and `@Production` / `@Staging` aliases (not deprecated stages API)
- FastAPI loads from registry via `models:/<name>@Production` — not baked into the image
- `/model/info` endpoint (version, alias, load timestamp)
- `promote_model.py` script (alias swap, not stage transition)
- **Checkpoint met:** Register new version → swap `@Production` alias → live API picks it up (currently via pod restart; zero-downtime hot reload is a Week 6/7 stretch)

### Week 4: Cloud deployment 🟡 (local-only)
- K8s manifests: Deployment, Service, Ingress, ConfigMap, PVC, HPA
- Running on **minikube** with hostpath-provisioner
- Readiness/liveness probes wired up
- **Not done yet:** EKS/GKE deploy, GitHub Actions auto-deploy on merge to main, public URL
- **Revised checkpoint:** API reachable via `minikube tunnel`, manifests are cloud-portable. Public-URL checkpoint moves to Fri 2026-06-13.

### Week 5: Auth + security ⬜ (next — Wed 2026-06-11)
- JWT auth middleware (HS256 to start; consider RS256 if asymmetric keys add value)
- API key management endpoints (create, revoke, list)
- Rate limiting: 100 req/min per key (token bucket, in-memory first, Redis if we get there)
- TLS via cert-manager + Let's Encrypt (once public) — for local, self-signed via mkcert
- Role-based access: admin vs user keys
- Input sanitization (length caps, charset whitelist)
- Security headers (CORS, HSTS, X-Content-Type-Options, X-Frame-Options)
- **Checkpoint:** unauthenticated → 401, over-quota → 429, all traffic TLS, integration tests cover both failure paths

### Week 6: Monitoring + observability ⬜ (weekend 2026-06-14)
- Prometheus scraping `/metrics` from FastAPI (`prometheus-fastapi-instrumentator`)
- Custom metrics: `prediction_latency_seconds`, `predictions_total`, `model_version_info`
- Model metrics: prediction distribution, confidence histogram, drift signal (PSI or KL vs reference window)
- Grafana dashboards: API performance, model health, cost estimates
- Alert rules: latency p95 > 500ms for 5min, error rate > 5%, drift detected
- **Checkpoint:** Live dashboard with real-time metrics; a triggered alert lands somewhere visible (Slack webhook or Discord)

### Week 7: Load testing + optimization ⬜ (weekend 2026-06-15)
- Locust scripts with realistic traffic patterns (steady-state, ramp, spike)
- Measure: max RPS, p50/p95/p99 latency, breaking point, error rate at breaking point
- Optimize: response caching, request batching (dynamic batching with `asyncio.Queue`), tune HPA targets, gunicorn worker count
- Re-test after each optimization, keep a changelog
- Cost estimate: $/1000 predictions at steady load
- **Checkpoint:** Load test report with before/after numbers and one clearly-attributable win

### Week 8: README + demo + blog ⬜ (Mon 2026-06-16)
- README: architecture diagram, design decisions, tradeoffs, scale considerations, "what I'd improve"
- One-command quick start (`docker-compose up` should genuinely work)
- 2–3 min Loom demo
- Blog post on **one** interesting problem (top candidate: the MLflow artifact saga)
- CI badges, license, contribution guide
- **Checkpoint:** A stranger is impressed within 30 seconds of opening the repo

## Key design decisions (with tradeoffs — for interview prep)

Each decision below has a "what I'd say in an interview" framing.

### FastAPI over Flask
- **Why:** Async by default, Pydantic schema validation, auto OpenAPI docs, ASGI lets us use a single worker with high concurrency for I/O-bound model loads.
- **Tradeoff:** Smaller ecosystem than Flask; ASGI debugging is less familiar to teams used to WSGI. For a CPU-bound model on a single pod, the async win is modest — the real win is the Pydantic + OpenAPI ergonomics.
- **When I'd reconsider:** If we needed deep integration with a legacy WSGI shop, or if the model were CPU-bound enough that async added no value.

### MLflow over DVC / SageMaker Model Registry / custom
- **Why:** Self-hostable, free, separates tracking from registry from artifacts cleanly, alias system lets us swap production pointers without redeploying.
- **Tradeoff:** Operational burden — we run the server, manage the artifact store, deal with the `mlflow-skinny` vs `mlflow[server]` footgun. SageMaker Registry would be one less moving piece on AWS.
- **When I'd reconsider:** If we were already AWS-native and a managed registry's lock-in cost was acceptable.

### Multi-stage Docker builds
- **Why:** Builder stage installs and compiles, runtime stage copies only artifacts. Final image is ~400MB vs ~1.2GB single-stage. Smaller image = faster pod startup = better autoscaling responsiveness.
- **Tradeoff:** Slightly slower local builds (no shared layers between stages), more complex Dockerfile.
- **What I measured:** TODO record before/after image size and cold-start times in Week 7.

### K8s over plain Docker / ECS / Cloud Run
- **Why:** K8s is the lingua franca of infra roles. Manifests are portable across EKS/GKE/AKS/minikube. HPA, probes, rolling updates, and service mesh integration come "for free".
- **Tradeoff:** Operational complexity is real — we hit it immediately with PVCs, artifact paths, and the minikube hostpath quirks documented below. For a single model with low traffic, Cloud Run would be cheaper and simpler.
- **When I'd reconsider:** Single-tenant low-traffic deployment with no need for sidecars/HPA.

### Custom auth over Auth0 / Cognito / Okta
- **Why:** This is a portfolio piece — the security engineering depth IS the point. JWT for stateless user auth, API keys for machine-to-machine, token-bucket rate limit because it's the canonical algorithm.
- **Tradeoff:** Custom auth is a footgun in real production. Token rotation, revocation, secret management, replay attacks — all of these are solved problems Auth0 handles. I'd never roll my own at a real job.
- **What I'd say in an interview:** "I built it from scratch to understand the primitives — JWT signing, bcrypt vs argon2, token-bucket vs leaky-bucket. In production I'd use Auth0 or Cognito and own only the API-key surface."

### Prometheus + Grafana over Datadog / New Relic
- **Why:** Free, self-hostable, industry standard, exposes me to PromQL — which is the actual interview-relevant skill.
- **Tradeoff:** No magic. We own the storage, the retention policy, the federation, the alertmanager config. Datadog gives you all of that and APM tracing for $.
- **What I'd say:** "Knowing PromQL transfers; knowing the Datadog UI doesn't."

### Locust over k6 / JMeter
- **Why:** Python-native (no second language for a small project), HTML reports look clean in a README.
- **Tradeoff:** Slower per-worker than k6 (k6 is Go). For 100k+ RPS testing, k6 wins; at our scale, Locust is fine.

### Token-bucket rate limiting over fixed-window / sliding-window
- **Why:** Smooths bursts gracefully (a key with 100/min can spend all 100 in one second if it has the budget), well-understood algorithm, easy to explain in interviews.
- **Tradeoff:** State is per-key — in-memory works for a single replica, but as soon as we scale to 2+ pods, we need Redis or sticky sessions. Documenting this as a known limitation. Redis needs to be implemented later on the weekend as well (remind)

### Alias-based model promotion over stages
- **Why:** MLflow deprecated `stages=["Production"]` in 2.9. Aliases (`@Production`, `@Staging`) are the supported path and give us multiple concurrent labels (e.g. `@Canary` alongside `@Production`).
- **Tradeoff:** Older tutorials still use stages — I've had to learn to translate. Migration cost is real if you have automation depending on stage transitions.

## What this project proves in interviews

- I can take a model from a trained artifact to a running production service with full automation
- I understand model lifecycle management — versioning, aliasing, promotion, rollback
- I can build a secure API surface — auth, rate limiting, input validation, TLS
- I can instrument an ML system and reason about its operational health
- I can identify and fix performance bottlenecks under load
- I think about cost, scale, and reliability — not just correctness
- I can debug across the Python / Docker / Kubernetes / storage stack without giving up
- I can write production-quality documentation that a stranger can act on

## Common interview questions this prepares you for

### ML systems
1. "How would you deploy an ML model to production?" → Walk through the whole pipeline
2. "How do you handle model versioning and promotion?" → MLflow registry + aliases, blue/green with `@Production` swap
3. "What happens when your model degrades in production?" → PSI drift detection, alert thresholds, automated rollback story
4. "How would you do a canary or A/B deployment of two model versions?" → Two aliases, weighted ingress routing, Prometheus labels by version
5. "Walk me through what happens when a request hits `/predict`" → Ingress → auth middleware → rate limit → Pydantic → model `.predict()` → Prometheus histogram → response

### Infra / systems
6. "Explain a Kubernetes deployment, service, and ingress" → Pod template, ClusterIP selector, L7 routing
7. "What's a readiness probe vs a liveness probe, and what happens if you swap them?" → Liveness restart loop, readiness traffic blackhole
8. "How does a multi-stage Docker build work?" → Builder + runtime, `COPY --from`, final image size implications
9. "Walk me through an OOMKill" → Exit 137 = SIGKILL from kernel OOM killer, not a Python exception, debug via `kubectl describe pod`
10. "How do PersistentVolumes work in K8s?" → PV/PVC binding, StorageClass, hostpath vs cloud-provider provisioners

### Security
11. "How do you secure a public ML API?" → JWT + API keys + rate limiting + TLS + input length caps
12. "JWT vs session tokens — when would you pick which?" → Stateless vs stateful, revocation tradeoffs
13. "How does a token bucket work? What breaks when you scale to multiple replicas?" → Per-key state, shared store (Redis) or sticky routing
14. "Why bcrypt/argon2 over SHA-256 for passwords?" → Work factor, salt, slow-by-design

### Observability / performance
15. "What metrics would you put on a model serving dashboard?" → RED (rate/errors/duration) + USE + ML-specific (prediction distribution, confidence histogram, drift)
16. "Tell me about a performance problem you debugged" → Load test ceiling, where the latency budget went, what you changed
17. "How would you reduce p99 latency for a model API?" → Caching, batching, model quantization, HPA tuning, async I/O on the request path
18. "What's the difference between p50 and p99, and why do we care about both?" → Median user vs worst-case user, tail latency matters under load

### MLOps-specific
19. "How do you detect model drift in production?" → PSI/KL on input distribution, prediction distribution, ground-truth lag problem
20. "How would you roll back a bad model?" → Alias swap to previous version, ideally without a redeploy
21. "Tell me about a hard infra bug you debugged" → Use the MLflow artifact saga below — it's a story across five layers of the stack

---

## Debugging Log: MLflow artifact registration (Weeks 3–4)

This was the hardest single problem in the project. Five layers of the stack failed in sequence, each masking the next. Below is structured for interview retrieval.

### Bug 1 — `mlflow-skinny[db]` won't run a tracking server
| | |
|---|---|
| **Symptom** | MLflow pod in `CrashLoopBackOff`, logs show `ModuleNotFoundError: gunicorn` or missing Flask deps |
| **Root cause** | `mlflow-skinny` is the **client** package — it deliberately omits the server entry point dependencies (gunicorn, Flask, alembic migrations) |
| **Fix** | Switch base image to `mlflow[server]` |
| **Interview takeaway** | Read the package's extras carefully. `skinny` in a package name almost always means "client only" |

### Bug 2 — `kubectl port-forward` dies mid-upload of a 268MB artifact
| | |
|---|---|
| **Symptom** | `mlflow.log_model` over `kubectl port-forward` aborts with `MLFLOW_HTTP_REQUEST_TIMEOUT` |
| **Root cause** | `port-forward` builds an HTTP/2 SPDY tunnel through the API server — it's a debug tool, not a data pipeline. The MLflow client's `MLFLOW_HTTP_REQUEST_TIMEOUT` env var is **client-side only**; the proxy ignores it |
| **What I tried first** | Bumped `MLFLOW_HTTP_REQUEST_TIMEOUT` — no effect, because the timeout was downstream |
| **Fix** | Don't push large artifacts through port-forward. Either run the registration step inside a pod or write directly to the PVC |
| **Interview takeaway** | `kubectl port-forward` is for interactive debugging. For bulk data, use a Job, sidecar, or volume write |

### Bug 3 — `kubectl cp` exits 137 (OOMKilled)
| | |
|---|---|
| **Symptom** | `kubectl cp model.bin pod:/path` dies with exit code 137, no Python stack trace |
| **Root cause** | `kubectl cp` shells out to `tar` **inside the destination pod**. The pod's 1Gi memory limit can't hold both the model and the tar buffer. Exit 137 = SIGKILL from the kernel OOM killer — not catchable, no stack trace |
| **Fix** | Stop using `kubectl cp` for files larger than a fraction of the pod memory limit |
| **Interview takeaway** | Exit 137 is the OOM killer fingerprint. Confirm via `kubectl describe pod` → `Reason: OOMKilled`. The fact that `kubectl cp` runs tar inside the receiving container is non-obvious and a frequent footgun |

### Bug 4 — `minikube cp` hangs indefinitely with no progress
| | |
|---|---|
| **Symptom** | `minikube cp ./artifacts /path/in/vm` hangs forever, no output |
| **Root cause** | `minikube cp` of a directory has no progress signalling and degrades badly on many small files |
| **Fix** | Bypass `minikube cp` entirely: `docker exec -i minikube bash -c 'cat > /tmp/hostpath-provisioner/default/mlflow-pvc/path'` writes the file straight into the minikube VM filesystem |
| **Interview takeaway** | Hostpath-provisioner PVCs are just files in the node's filesystem (`/tmp/hostpath-provisioner/<ns>/<pvc>/` in minikube's VM). Visible via `minikube ssh` or `docker exec minikube ls`. Once you know this, you can move data around freely |

### Bug 5 — `No such artifact: ''` even after the file is on the PVC
| | |
|---|---|
| **Symptom** | API pod can't load the model. MLflow throws `No such artifact: ''` |
| **Root cause (1 of 2)** | The MLflow server's artifact proxy was looking at `./mlartifacts` (the **default** `--artifacts-destination`, relative to cwd `/`) instead of `/mlflow/artifacts` where the PVC was actually mounted |
| **Root cause (2 of 2)** | The model version's `source` and `storage_location` columns in the SQLite registry were written as local POSIX paths (`/mlflow/artifacts/0/...`) during the initial docker-compose registration. This made MLflow resolve them via `LocalArtifactRepository`, reading from the **API pod's** filesystem — where the PVC isn't mounted |
| **Fix** | (a) Add `--artifacts-destination file:///mlflow/artifacts` to the MLflow server command. (b) Rewrite the SQLite rows from `/mlflow/artifacts/...` to `mlflow-artifacts:/0/<run_id>/artifacts/<name>` so MLflow uses `HttpArtifactRepository` against the server's proxy |
| **Interview takeaway** | MLflow has two artifact retrieval paths: **direct filesystem** (`source` is a local URI) and **HTTP proxy** (`source` is `mlflow-artifacts:/...`). The registry remembers whichever was active **at registration time**. Mix them and nothing works until you rewrite the column |

### Bug 6 — Loader using deprecated stages API
| | |
|---|---|
| **Symptom** | After all the above, the loader returned no versions when filtering by `stages=["Production"]` |
| **Root cause** | New versions were tagged with the `@Production` **alias**, not the deprecated stage. MLflow 2.9+ deprecated stages |
| **Fix** | Switch to `models:/<name>@Production` URI + `get_model_version_by_alias("Production")` |
| **Interview takeaway** | Watch for deprecation between MLflow 2.x minor versions. Aliases are strictly better — you can have `@Production` and `@Canary` on different versions simultaneously |

### The 60-second interview version

> "I was getting a 268MB HuggingFace model from MLflow's registry into a Kubernetes-served FastAPI, and it failed in five different ways before I got it working. The tracking server itself crash-looped because the image was `mlflow-skinny`, which is the client package and doesn't include gunicorn. Once that was fixed, `kubectl port-forward` died mid-upload because it's an HTTP/2 debug tunnel, not a data pipeline, and the MLflow client's timeout env var is client-side only. `kubectl cp` got OOMKilled — exit 137 — because `kubectl cp` runs tar inside the destination pod against its memory limit. I ended up writing the file directly into the minikube VM with `docker exec`, into the hostpath-provisioner directory where the PVC is actually mounted. Then the API pod still couldn't load it because MLflow's artifact proxy was looking at the wrong path on disk — `--artifacts-destination` defaults to a relative path — AND the version row in SQLite had a local-filesystem URI, so MLflow was using `LocalArtifactRepository` against the API pod's filesystem instead of going through the proxy. I had to rewrite the rows to use `mlflow-artifacts:/` URIs. The thing I'd never forget: exit 137 is the OOM killer, not a Python exception, and MLflow's registry remembers which artifact retrieval path was active at registration time."

### Things this story demonstrates

- Reading symptoms across language, container, network, and storage layers
- Knowing when to stop fighting a tool (`kubectl cp`) and use a different one (`docker exec`)
- Reading source/docs carefully — the `--artifacts-destination` default vs the `--default-artifact-root` flag is a real footgun and you only catch it by reading the server's argument parser
- Direct database surgery (SQLite UPDATE on the registry) when the supported migration path doesn't exist
- Persistence: each of these failures looked like the last one, and each had a different root cause
