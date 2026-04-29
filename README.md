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

- **Hugging Face Space**: https://huggingface.co/spaces/ipreencekmr/agentic-chess
- **Live App**: https://ipreencekmr-agentic-chess.hf.space
- **Jaeger Tracing UI**: https://ipreencekmr-agentic-chess.hf.space/jaeger

<img width="1917" height="948" alt="image" src="https://github.com/user-attachments/assets/2bc8520b-cf5f-469d-85cd-453876025444" />

<img width="1918" height="941" alt="image" src="https://github.com/user-attachments/assets/35138ec2-e519-48ab-8790-6199939c4768" />

## Agent Tracing

<img width="1917" height="940" alt="image" src="https://github.com/user-attachments/assets/eab80a46-ce79-481e-afd3-8088729ab080" />

## Docker Compose 

<img width="1023" height="336" alt="Screenshot 2026-04-28 at 8 17 46 PM" src="https://github.com/user-attachments/assets/c85b0d6d-819e-4834-984b-191cdba2e221" />

## API Tracing using Jaeger

<img width="1470" height="605" alt="Screenshot 2026-04-28 at 8 19 46 PM" src="https://github.com/user-attachments/assets/e38178f2-4858-492c-a2c0-d2791347239c" />

<img width="1470" height="584" alt="Screenshot 2026-04-28 at 8 19 12 PM" src="https://github.com/user-attachments/assets/da72451e-21c9-416e-9ec1-ab70655c269d" />

## Project Structure

- `backend/` FastAPI API and chess engine orchestration
- `frontend/` React UI with split components/hooks/services
- `docker-compose.yml` local multi-container orchestration
- `Dockerfile` Hugging Face Docker Space image (frontend + backend in one container)
- `.github/workflows/deploy-huggingface-space.yml` GitHub Actions deployment workflow
- `.github/workflows/readme-agent.yml` GitHub Actions workflow for automated README updates
- `.github/workflows/code-cleanup.yml` new weekly automated code cleanup and refactor workflow powered by OpenAI, now supports dry-run mode for previewing changes without writing files or opening PRs

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
- Piece movement animation: `0.5s` (reduced from 2s for smoother UX)
- Fullscreen board supported
- Visual check indicator: red pulsing highlight on king's square when in check
- Mobile tap-to-move shows selected piece highlight and legal move dots
- Piece promotion logic fixed to avoid king drag triggering promotion flow

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
CLEANUP_MODEL=gpt-4.1
```

Notes:
- `.env` is auto-loaded by backend startup.
- `CHESS_ENGINE_MOVE_TIME` is in milliseconds and clamped to `100` - `5000` ms.
- `STOCKFISH_PATH` must point to a valid Stockfish binary.
- Langchain tracing environment variables enable detailed AI agent tracing.
- `CLEANUP_MODEL` sets the OpenAI model used for weekly automated code cleanup.
- The weekly code cleanup workflow now supports a dry-run mode to preview changes without writing files or opening PRs.
- The code cleanup workflow now reads `CLEANUP_MODEL` from GitHub Variables (`vars.CLEANUP_MODEL`) instead of secrets.

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
- New GitHub Actions workflow `.github/workflows/readme-agent.yml` automates README updates on code changes and adds `ai-generated` label to PRs.
- New GitHub Actions workflow `.github/workflows/code-cleanup.yml` added for weekly automated code cleanup and refactor, running every Monday and on manual trigger, using OpenAI to fix lint issues and improve code quality.
- The code cleanup workflow now supports a `dry_run` input to preview changes without writing files or opening PRs.
- Default `STOCKFISH_PATH` in Docker Compose is set to `/usr/games/stockfish`.
- Piece promotion logic fixed to avoid king drag triggering promotion flow.
- Check state is visually indicated on the board with a red pulse on the king's square.
- Mobile tap-to-move UX improved with selected piece highlight and legal move dots.
- Piece movement animation duration reduced to 0.5 seconds for smoother gameplay experience.
