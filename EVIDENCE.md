# Evidence

This file is the proof pack for the official FlyRank capstone requirements in Section 6 and behavioral probes in Section 13 of the supplied brief.

**Rule:** do not mark a check complete until the real command/API call has been run and its output pasted below. The initial repository contains synthetic SVG illustrations; results on them do not establish real-world image accuracy.

Detailed task-to-code mapping: [FlyRank requirements and evidence matrix](docs/flyrank-requirements-matrix.md).

## Environment and automated tests

- [ ] Record OS/Python version and exact command used.
- [ ] `python -m pytest -q` — paste actual output.
- [ ] Record the commit SHA tested.
- [ ] `GET /health` — paste status and JSON response.
- [ ] `GET /docs` — record HTTP status.

## Section 6 — AI processing

- [ ] **S6-AI-1:** Paste a schema-valid vision result and a test/transcript proving malformed model output is rejected or flagged.
- [ ] **S6-AI-2 / Probe P1:** Paste a low-confidence image ID, confidence value and flagged response.
- [ ] **S6-AI-3 / Probe P1:** Paste batch job creation, progress/status, retry attempt and final result/failure behavior.
- [ ] **S6-AI-4 / Probe P6:** Paste cost-ledger entries for individual vision and embedding/similarity calls, including a failed call if testable.

## Section 6 — Matching and mismatch guard

- [ ] **S6-MATCH-1:** Show stored embedding/vector representation and ranked API response. State whether the active implementation is lexical baseline or real embeddings.
- [ ] **S6-MATCH-2:** Demonstrate equivalent-concept matching (for example “red fox” / “Vulpes vulpes”) using a labeled test.
- [ ] **S6-GUARD-1 / Probe P3:** Paste the wolf-as-candidate-for-fox-post rejection response and mismatch explanation.
- [ ] **S6-GUARD-2:** Paste a rejected match showing human-readable reasons.
- [ ] **S6-GUARD-3 / Probe P4:** Paste a no-suitable-image response with `no_confident_match` and rejection reasons.
- [ ] **Probe P2:** Paste the red-fox post ranking showing fox first and wolf/dog lower.

## Section 6 — Backend and review

- [ ] **S6-BACKEND-1:** Document database tables, indexes, persistence behavior and whether schema migrations are provided.
- [ ] **S6-BACKEND-2:** Paste review API approve and reject responses; show how the reviewer inspects the rationale.
- [ ] **Shared #2:** Paste invalid-input examples returning expected 4xx responses rather than 500.
- [ ] **Shared #3:** Paste evidence of background processing, retries and surfaced failure behavior.
- [ ] **Shared #5:** Demonstrate idempotent behavior for a retried operation where it matters.
- [ ] **Shared #7 / Probe P6:** Demonstrate per-call cost attribution and explain whether a hard budget guard exists.

## Section 6 — Quality and documentation

- [ ] **S6-QUALITY-1 / Probe P5:** Paste real output from `python scripts/evaluate.py` (or the documented equivalent), including evaluated count, correct top-1 count and top-1 precision.
- [ ] Update README with the **measured** top-1 precision from that run; keep the synthetic/real dataset caveat next to the metric.
- [ ] **S6-QUALITY-2:** Confirm required files exist and follow Windows setup + seed instructions from a clean environment.
- [ ] Record failed probes, known limitations and next fixes. Do not hide failed or incomplete checks.

## Actual run transcripts

Paste date/time, commit SHA, command/request and unedited relevant output below. Redact tokens and private data.

### Test suite

_Not run and captured in this evidence file yet._

### Health and API docs

_Not run and captured in this evidence file yet._

### Batch job and confidence flags

_Not run and captured in this evidence file yet._

### Matching probes P2–P4

_Not run and captured in this evidence file yet._

### Evaluation probe P5

_Not run and captured in this evidence file yet._

### Cost probe P6

_Not run and captured in this evidence file yet._
