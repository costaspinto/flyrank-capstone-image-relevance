# FlyRank Capstone — AI Image Understanding & Content Matching Engine

A Python/FastAPI capstone that classifies images into structured metadata, ranks images for article content, and rejects weak or mismatched recommendations with explicit reasons.

## Windows quick start
1. Extract this ZIP into `C:\Projects\flyrank-capstone-image-relevance`.
2. Open PowerShell in that folder.
3. Run:
   ```powershell
   Set-ExecutionPolicy -Scope Process Bypass
   .\scripts\Setup-Windows.ps1
   ```
4. Open `http://127.0.0.1:8000/docs`.

Later, start it with `.\scripts\Run-Windows.ps1`. Run tests with `.\.venv\Scripts\python.exe -m pytest -q`.

## Features
- FastAPI routes, SQLAlchemy persistence, schema validation.
- Gemini REST and Ollama vision provider options.
- Local lexical baseline and optional Ollama embeddings.
- Image batch job with retries/progress, confidence flags, per-call cost ledger.
- Mismatch guard with human-readable reasons, review API, evaluation script.
- A seed script that generates 40 synthetic SVG demo assets across five animal subjects and 10 demo articles.
- Required `capstone.yaml`, `EVIDENCE.md`, `BUILDLOG.md`, `.env.example`, MIT license.

## Important honesty note
The 40 included assets are synthetic SVG illustrations, not licensed photographs. They make the API and guard reproducible, but they do **not** prove real-world vision accuracy. Before submission, add at least 40 licensed-free photographs, run Gemini/Ollama classification, label 10+ article/image matches, tune thresholds, and paste actual outputs into `EVIDENCE.md`.

The default lexical vectorizer is a zero-setup baseline, not a trained semantic embedding model. Ollama embeddings can be enabled in `.env`. The worker runs in-process and is intended for a single-instance capstone, not production scale.

## Configuration
Copy `.env.example` to `.env` (the setup script does this). Defaults run locally without a key.
- Gemini: `VISION_PROVIDER=gemini`, add `GEMINI_API_KEY`.
- Ollama vision: `VISION_PROVIDER=ollama`, configure `OLLAMA_BASE_URL` and `OLLAMA_VISION_MODEL`.
- Ollama embeddings: `EMBEDDING_PROVIDER=ollama`, configure `OLLAMA_EMBEDDING_MODEL`.

All keys belong in `.env`, never in Git. Cost ledger values are configured estimates, not invoices.

## API
`GET /health`, `GET /api/images`, `POST /api/images`, `POST /api/jobs/vision`, `GET /api/jobs/{job_id}`, `POST /api/posts`, `GET /api/posts/{post_id}/images`, `POST /api/matches/guard`, `POST /api/reviews`, `GET /api/costs`, `POST /api/evaluation/run`. Interactive docs: `/docs`.

## Architecture
Image corpus → batch job → vision provider → Pydantic validation → metadata/confidence flag.
Article text + image captions → similarity ranking → mismatch guard → accepted suggestion or `no_confident_match` with reasons → human review API.
