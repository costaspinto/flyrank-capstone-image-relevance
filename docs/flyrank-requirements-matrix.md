# FlyRank Capstone Requirements & Evidence Matrix

**Source of truth:** *AI Image Understanding & Content Matching Engine — FlyRank Internship, Backend Track, Capstone Brief*, Sections 6, 8, 11 and 13.

This maps the official requirements and acceptance probes to this repository. Statuses reflect code/document inspection, not an external FlyRank evaluator result. A requirement is not complete until reproducible evidence is added to `EVIDENCE.md`.

## Section 6 — Official capstone requirements

| ID | Official requirement | Implementation pointers | Status / evidence required |
|---|---|---|---|
| S6-AI-1 | Vision output is structured and schema-validated; invalid responses are never trusted | `app/providers.py`, `app/schemas.py`, `app/jobs.py` | Partially evidenced — add a test/transcript proving malformed provider output is rejected or flagged. |
| S6-AI-2 | Low-confidence classifications are flagged instead of accepted | `app/main.py`, `app/guard.py`, `app/config.py`, `tests/test_guard.py` | Guard logic/test exist; paste a real low-confidence image ID and response. |
| S6-AI-3 | Images are processed through a batch background job with retries | `app/jobs.py`, `app/main.py`, `app/models.py` | Implementation exists by inspection; capture progress, retries and final status. |
| S6-AI-4 | Vision and embedding costs are tracked per call | `app/jobs.py`, `app/service.py`, `app/models.py`, `/api/costs` | Cost ledger exists by inspection; capture both vision and similarity/embedding entries, including failures if testable. |
| S6-MATCH-1 | Image/post embeddings are stored; posts return ranked image suggestions | `app/embeddings.py`, `app/service.py`, `app/main.py` | Gap to validate: default similarity is lexical, not a trained semantic embedding/vector index. Validate acceptance or implement real embeddings in the primary path. |
| S6-MATCH-2 | Semantic matching recognizes equivalent concepts such as “red fox” and “Vulpes vulpes” | `app/embeddings.py`, `app/service.py`, `data/eval_set.json` | Not evidenced; add labeled synonym/concept cases and report measured results. |
| S6-GUARD-1 | Guard rejects incorrect recommendations; wolf-on-fox scenario fails | `app/guard.py`, `tests/test_guard.py`, `POST /api/matches/guard` | Unit test exists; paste actual test output and API response. |
| S6-GUARD-2 | Rejections include a human-readable explanation | `app/guard.py`, `app/service.py` | Logic exists by inspection; paste a rejected candidate response and reasons. |
| S6-GUARD-3 | No match above threshold returns “no confident match” with reasons | `app/service.py`, `app/guard.py` | Logic exists by inspection; capture a no-match article response. |
| S6-BACKEND-1 | Database models for images, tags, embeddings, posts, suggestions, approvals/rejections, with required indexes | `app/models.py`, `app/database.py` | Needs schema audit: verify embedding persistence, indexes, migrations and whether all required entities are represented. |
| S6-BACKEND-2 | API endpoints validated; review approve/reject/inspect-why workflow exists | `app/main.py`, `app/schemas.py`, `app/models.py` | Partially evidenced; add endpoint tests for review approve/reject, invalid-input 4xx, and explanation inspection. |
| S6-QUALITY-1 | Labeled evaluation dataset measures top-1 precision; number appears in README | `data/eval_set.json`, `app/evaluation.py`, `scripts/evaluate.py`, `README.md` | Not evidenced; run evaluation, then add the measured metric with synthetic-data caveat. Do not invent a number. |
| S6-QUALITY-2 | README explains architecture and diagram; required files exist | `README.md`, `docs/architecture.md`, `capstone.yaml`, `EVIDENCE.md`, `BUILDLOG.md`, `.env.example` | Files exist; validate setup from a clean environment and ensure docs describe the active provider/configuration. |

## Section 8 — Official phase gates

| Phase | Official gate | Evidence to attach |
|---|---|---|
| 1 — Design | One-page design document committed | Data model, API surface, matching/guard rules, dataset plan, explicit non-goal. |
| 2 — Image understanding | All images tagged by batch job; costs visible | Batch output, schema-valid records, low-confidence flag, retry behavior, per-call cost ledger. |
| 3 — Matching engine | Fox post ranks fox first; guard refuses wolf | Fox-post ranking, wolf rejection, no-match response, semantic-equivalence case. |
| 4 — Production layer | Review API and eval dataset; measured precision | Review approve/reject transcripts, evaluation output, README metric matching output. |

## Section 13 — Official behavioral acceptance probes

| Probe | Acceptance criterion | Status |
|---|---|---|
| P1 | Batch job gives every image schema-valid tags; at least one low-confidence image is flagged | Evidence pending |
| P2 | Red-fox article ranks fox first; wolf and dog rank clearly lower | Evidence pending |
| P3 | Forced wolf candidate is rejected with category/subject mismatch explanation | Guard unit test exists; API evidence pending |
| P4 | No-suitable-image query returns no-confident-match plus reasons | Evidence pending |
| P5 | Evaluation script reports top-1 precision matching README | Evidence pending; do not publish an unmeasured metric |
| P6 | Cost log attributes every vision/embedding call with a cost entry | Evidence pending |

## Shared backend requirements — official list in Section 13

| # | Requirement | Code pointers | Status / follow-up |
|---|---|---|---|
| 1 | Layered architecture — data / logic / HTTP separated | `app/models.py`, `app/service.py`, `app/main.py` | Partially present; document layer boundaries. |
| 2 | Boundary validation — bad input returns clean 4xx, never 500 | `app/schemas.py`, `app/main.py` | Not fully evidenced; add invalid-input tests and verify error handling. |
| 3 | At least one background job; retries + failure alert | `app/jobs.py`, `app/main.py` | Background job present; verify retry and surfaced failure behavior. |
| 4 | Real persistence; schema as migrations, correct indexes, isolated tenants | `app/database.py`, `app/models.py` | Gap/risk; inspect migrations, indexes and tenant isolation. Local SQLite/single-instance scope may not satisfy every phrase. |
| 5 | Idempotency where it matters | `app/main.py`, `app/jobs.py` | Not evidenced; test duplicate/retried operations. |
| 6 | Secrets via environment only; never logged | `.env.example`, `.gitignore`, `app/config.py`, `app/providers.py` | Basic repository hygiene was checked; broader secret/log review remains required. |
| 7 | AI cost tracked per call with a budget guard | `app/models.py`, `app/jobs.py`, `app/service.py`, `/api/costs` | Cost ledger appears present; verify end-to-end attribution and whether a hard budget guard exists. |

## Dataset and model caveats

The current seeded assets are synthetic SVG illustrations, not licensed photographs; they do not establish real-world vision accuracy. The default similarity baseline is lexical, not a trained semantic embedding model. Keep these limitations visible until the implementation is upgraded and probes rerun.

## Evidence rules

- Paste actual command output, test output and API JSON into `EVIDENCE.md`.
- State whether each result used synthetic SVGs or licensed photographs.
- Record provider/model, latency and configured/estimated cost when relevant; never expose API keys.
- Report only measured evaluation numbers; synchronize the README metric with the evaluation output.
- Passing unit tests alone does not prove all six behavioral probes pass.
