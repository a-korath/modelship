# Handoff Document — Week 5 Next, Sprint Plan Locked

## Status

Weeks 1, 3, 4 complete. Week 2 (CI/CD) deferred. Week 5 (Auth + Security) is the immediate next task.

Last smoke test (from handoff-001.md):
```
GET  /health  → {"status":"ok","model_loaded":true}
POST /predict → POSITIVE 0.9999  ("I love this!")
POST /predict → NEGATIVE 0.9996  ("This is terrible.")
GET  /model/info → model_loaded: true, loaded_at: 2026-06-01T00:42:34
```

## Sprint Plan (agreed this session)

| Date | Work |
|------|------|
| Wed 2026-06-11 | Week 2: CI/CD pipelines (GitHub Actions lint→test→build→push, git SHA tagging, Makefile, branch protection) + Week 5: Auth + Security if time permits |
| Fri 2026-06-13 | AWS EKS setup — move cluster from minikube to managed K8s, get a public URL |
| Weekend 2026-06-14–15 | Week 6: Monitoring (Prometheus + Grafana) + Week 7: Load testing + optimisation — project goes live |
| Mon 2026-06-16 | Week 8: README, Loom demo, blog post, CI badges — project fully shipped |

## What Happened This Session

1. **project1_modelship.md was reviewed and improved by an Opus 4.7 subagent.** The improved version was generated in conversation but **was NOT written back to disk** — the file on disk is still the original. The improved version includes:
   - `Current Status` section at the top
   - `K3s` → `minikube` correction in tech stack
   - Week 4 checkpoint corrected (still local, not public URL)
   - Week 2 deferral rationale documented
   - Design decisions expanded with tradeoffs + "what I'd say in an interview" framing
   - Interview questions expanded from 7 → 21, organized by category
   - Debugging log restructured into a 6-bug table with Symptom / Root cause / Fix / Interview takeaway
   - 60-second interview version of the MLflow saga added

   **Written to disk** at end of session. `project1_modelship.md` is now the improved version.

2. **Memory updated** with the sprint plan and week corrections.

## Week 2 Scope (CI/CD — start here Wednesday)

Files to create/fill in:
- `.github/workflows/ci.yml` — ruff lint → pytest → docker build → push to registry
- `.github/workflows/deploy.yml` — deploy to K8s on merge to main
- `Makefile` — `make build`, `make test`, `make run`, `make push`, `make deploy`

Features:
- Image tagged with git SHA (`ghcr.io/<user>/modelship:<sha>`)
- Branch protection: CI must pass before merge
- Smoke test step in deploy workflow (curl /health after rollout)

Checkpoint: Every push triggers green pipeline; tagged image lands in registry.

## Week 5 Scope (Auth + Security)

Files to create/fill in:
- `src/api/middleware/auth.py` — JWT validation + API key management
- `src/api/middleware/rate_limit.py` — token bucket rate limiter (100 req/min per key)

Features:
- JWT auth middleware (HS256; validate on every request)
- API key endpoints: create, revoke, list
- Rate limiting: 100 req/min per key, token bucket algorithm
- Role-based access: admin vs. user keys
- Input sanitization (length caps, charset whitelist)
- Security headers (CORS, HSTS, X-Content-Type-Options, X-Frame-Options)
- TLS: self-signed via mkcert for local; cert-manager + Let's Encrypt once on EKS

Checkpoint: 401 for unauthenticated, 429 for rate-limited, all traffic TLS.

## Teaching Context

**Who:** 2027 new grad targeting ML Platform Engineer / MLOps roles. ModelShip is a depth portfolio project.

**Role:** Advisor, not assistant. Never do things for the user — help them figure out how to do things themselves. The distinction matters: an assistant produces output, an advisor builds capability.

**Teaching style:**
- For each concept: (1) The logic — how it works mechanically, (2) Why this decision — the tradeoff, (3) What it does — the observable effect
- Then provide the implementation. Explanation and code go together.
- After explanation + code: ask one targeted question to confirm understanding before moving on.
- Grilling sessions and interview simulations work well — use them often.

**Pacing:** One step at a time. Propose the next single step, wait for confirmation. Never bulk-scaffold files or directories.

**Interview coaching notes:**
- User hesitates before connecting pieces they already know — push them to complete the answer in one breath.
- Rollback story: change `@Production` alias in MLflow → rolling update picks it up — coach this answer.
- When asked "why did you build this?" — lead with the hot-reload consistency problem, not job market motivation.

## To Resume

```bash
minikube start
kubectl get pods  # wait for all 3 Running
kubectl port-forward svc/modelship-service 8000:8000
curl http://127.0.0.1:8000/health  # should show model_loaded: true
```

## Key Files

| File | What it is |
|------|-----------|
| `handoffs/handoff-001.md` | Full Week 3–4 debug log, MLflow artifact saga explanation |
| `project1_modelship.md` | Project spec, timeline, design decisions, interview prep (note: improved version not yet written to disk) |
| `src/api/middleware/auth.py` | Empty — Week 5 target |
| `src/api/middleware/rate_limit.py` | Empty — Week 5 target |
| `.github/workflows/` | Empty — Week 2 target |

## Suggested Skills for Next Session

- `/grill-me` — after implementing each Week 2 or Week 5 concept, run a grill to stress-test understanding before moving on
- `/handoff` — create handoff-003.md at end of Wednesday session to capture CI/CD + auth state before the AWS push
