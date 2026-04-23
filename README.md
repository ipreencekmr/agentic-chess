---
title: Agentic Chess
emoji: ♟️
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# Agentic Chess

React frontend + FastAPI backend chess application with drag-and-drop moves, named players, AI mode, and fullscreen board support.

<img width="1917" height="948" alt="image" src="https://github.com/user-attachments/assets/2bc8520b-cf5f-469d-85cd-453876025444" />

<img width="1918" height="941" alt="image" src="https://github.com/user-attachments/assets/35138ec2-e519-48ab-8790-6199939c4768" />

## Project Structure

- `backend/` FastAPI API and chess engine orchestration
- `frontend/` React UI with split components/hooks/services
- `docker-compose.yml` local multi-container orchestration
- `Dockerfile` Hugging Face Docker Space image (frontend + backend in one container)
- `.github/workflows/deploy-huggingface-space.yml` GitHub Actions deployment workflow

## Run Locally (Non-Docker)

Backend:

```bash
pip install -r requirements.txt
python app.py
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173` and proxies `/api` to `http://localhost:8000`.

For `Hard (Engine)` difficulty on local machine, install Stockfish and ensure either:

- `stockfish` is available on your system `PATH`, or
- set `STOCKFISH_PATH` environment variable to the engine binary path.

## Run With Docker Compose

```bash
docker compose up --build
```

App URL:

- `http://localhost:7860`

Optional OpenAI key:

```bash
# PowerShell
$env:OPENAI_API_KEY="sk-..."
docker compose up --build
```

Optional engine tuning:

```bash
# path to Stockfish binary if not on PATH
STOCKFISH_PATH=/usr/games/stockfish

# think time per move in seconds (0.1 to 5.0)
CHESS_ENGINE_MOVE_TIME=0.8
```

## Hugging Face Space Deployment (via GitHub Actions)

This repo includes:

- Root `Dockerfile` for Hugging Face Docker Space runtime
- Workflow: `.github/workflows/deploy-huggingface-space.yml`

### 1. Create a Hugging Face Space

- Space SDK: `Docker`
- Space visibility: your choice

### 2. Add GitHub repository secrets

In GitHub repo settings, add:

- `HF_TOKEN`: Hugging Face access token with write permissions
- `HF_SPACE_ID`: value like `username/space-name`

### 3. Deploy

- Push to `main` or run workflow manually from Actions tab.
- Workflow syncs repository contents to the Hugging Face Space Git repo.

## Notes

- In browser builds, frontend API base defaults to `/api`.
- Override API base manually with `VITE_API_BASE_URL` if needed.
