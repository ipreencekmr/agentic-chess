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

React frontend + FastAPI backend chess application with multiple AI difficulty modes, desktop drag play, mobile tap-to-move, and fullscreen board support.

## Live Demo

- Hugging Face Space: `https://huggingface.co/spaces/ipreencekmr/agentic-chess`

<img width="1917" height="948" alt="image" src="https://github.com/user-attachments/assets/2bc8520b-cf5f-469d-85cd-453876025444" />

<img width="1918" height="941" alt="image" src="https://github.com/user-attachments/assets/35138ec2-e519-48ab-8790-6199939c4768" />

## Agent Tracing

<img width="1917" height="940" alt="image" src="https://github.com/user-attachments/assets/eab80a46-ce79-481e-afd3-8088729ab080" />

## Project Structure

- `backend/` FastAPI API and chess engine orchestration
- `frontend/` React UI with split components/hooks/services
- `docker-compose.yml` local multi-container orchestration
- `Dockerfile` Hugging Face Docker Space image (frontend + backend in one container)
- `.github/workflows/deploy-huggingface-space.yml` GitHub Actions deployment workflow
- `.github/workflows/readme-agent.yml` GitHub Actions workflow for automated README updates

## Game Modes and Difficulty

- `Single Player`
- `Multiplayer`

Single Player difficulty options:
- `Easy` - level 1 
- `Medium` - level 8
- `Hard` - level 20
- `Capture Priority` (prefer captures, else random legal move)
- `AI Agent` (LLM-powered move using selected model with Langchain tracing)

Notes:
- `AI Agent` option appears only when backend has `OPENAI_API_KEY` available.
- `Easy`, `Medium`, `Hard` and `Capture Priority` do not use OpenAI even if key is present.
- In Single Player, your move is shown first, then agent move is called as a second step.
- Changing difficulty starts a fresh game automatically.

## Controls and UX

- Desktop: drag-and-drop piece movement
- Mobile/tablet: tap-to-move (tap source square, then destination square)
- Piece movement animation: `1.5s`
- Fullscreen board supported

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

Optional environment variables:

```bash
OPENAI_API_KEY=
STOCKFISH_PATH=
CHESS_ENGINE_MOVE_TIME=
LANGCHAIN_API_KEY=
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=
```

Notes:
- `.env` is auto-loaded by backend startup.
- `CHESS_ENGINE_MOVE_TIME` is in milliseconds and clamped to `100` - `5000` ms.
- `STOCKFISH_PATH` must point to a valid Stockfish binary.
- Langchain tracing environment variables enable detailed AI agent tracing.

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

For Linux
```bash
STOCKFISH_PATH=/usr/games/stockfish
CHESS_ENGINE_MOVE_TIME=1500
```

For Mac (Homebrew)
```bash
STOCKFISH_PATH=/opt/homebrew/bin/stockfish
CHESS_ENGINE_MOVE_TIME=1500
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
- Backend now uses a singleton `StockfishService` for engine management with skill level and depth tuning.
- AI Agent moves are powered by a Langchain-traced tool-enabled approach for better move selection and observability.
- New GitHub Actions workflow `.github/workflows/readme-agent.yml` automates README updates on code changes.