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