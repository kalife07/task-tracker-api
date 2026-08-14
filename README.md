# Task Tracker API

A learning-focused REST API built with Python and FastAPI, using JSON file storage f

## Prerequisites

- Python 3.12+

---

## 1. Create a virtual environment and install dependencies

**Linux/macOS**

```bash

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt


```

**Windows (PowerShell)**

```powershell

python -m venv venv

.\venv\Scripts\Activate.ps1

pip install -r requirements.txt


```

---

## 2. Configure environment variables

Copy the example file and adjust values as needed:

**Linux/macOS**

```bash

cp .env.example .env


```

**Windows (PowerShell)**

```powershell

Copy-Item .env.example .env


```

---

## 3. Start the server

**Linux/macOS**

```bash

uvicorn app.main:app --reload --port 8000


```

**Windows (PowerShell)**

```powershell

uvicorn app.main:app --reload --port 8000


```

The API will be available at `http://localhost:8000`.

Interactive docs (Swagger UI) are at `http://localhost:8000/docs`.

---

## 4. Test the health endpoint

```bash

curl -s [http://localhost:8000/health](http://localhost:8000/health)


```

Expected response:

```json

{

  "status": "ok",

  "timestamp": "2025-05-16T10:30:00.123456+00:00"

}


```

---

## Final Project

Branch reviewed: final-project

### What this submission demonstrates

- Existing Task Tracker app still runs inside the intended course scope.
- CI runs the pytest suite on push and/or pull request.
- Docker image builds and runs with /health returning 200.
- AI review, security, and ownership evidence is in docs/.

### How to run locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000

```

### How to run tests

```bash
pytest -v

```

Result: 18 passed, 0 failed. All tests pass, including `test_delete_existing_returns_204_no_body` and `test_delete_missing_returns_404`, which previously failed with HTTP 405 before the `DELETE /tasks/{id}` route was added to `app/api/routes/tasks.py`.

### How to run with Docker

```bash
docker build -t task-tracker .
docker run -p 8000:8000 task-tracker
curl -s http://localhost:8000/health

```

Result: `{"status": "ok", "timestamp": "2026-08-10T14:22:03.481920+00:00"}` (HTTP 200)

### Evidence files

- docs/release-evidence.md
- docs/final-ai-review.md
- docs/ai-playbook.md

### AI assistance summary

AI helped draft or review: CI workflow syntax, Dockerfile best practices, and a first pass at the security review checklist. I verified the work by: running the full pytest suite locally, manually hitting /health after the Docker build, and reading through the CI diff line-by-line before pushing. One AI suggestion I rejected or corrected: AI suggested adding `continue-on-error: true` to the pytest step in CI "to keep the pipeline green during development" — I rejected this because it would silently hide real test failures, which defeats the purpose of CI.