# Deploy Frontend + Backend on Vercel (Same Project)

This project is set up to deploy **both** the React frontend and FastAPI backend in a **single Vercel project** from the repo root.

## How it works

- **Build:** Vercel runs `pip install -r requirements.txt` then builds the frontend (`cd frontend && yarn install && yarn build`). The FastAPI app is the deployment entrypoint (via `pyproject.toml`).
- **Runtime:** One serverless function runs the FastAPI app. It serves:
  - `/api/*` → your API routes
  - `/*` → static files from `frontend/build` (React SPA)
- **Same origin:** The frontend uses relative URLs (`/api`), so leave `REACT_APP_BACKEND_URL` **unset** in Vercel.

## Deploy steps

1. **Import to Vercel**  
   [vercel.com/new](https://vercel.com/new) → Import your Git repo.  
   **Do not set** “Root Directory”; use the repo root.

2. **Environment variables** (Project Settings → Environment Variables)  
   Set these for the backend (required):

   | Name            | Description                    |
   |-----------------|--------------------------------|
   | `MONGO_URL`     | MongoDB connection string      |
   | `DB_NAME`       | Database name (e.g. `tti_db`)  |
   | `JWT_SECRET_KEY`| Secret for JWT (min 32 chars)  |
   | `STRIPE_API_KEY`| Stripe secret key              |

   **Do not set** `REACT_APP_BACKEND_URL` (same-origin `/api` is used).

3. **Deploy**  
   Push to your connected branch or trigger a deploy from the Vercel dashboard.

## Files involved

- **`vercel.json`** – build command (pip + frontend build)
- **`pyproject.toml`** – points Vercel to `backend.server:app`
- **`requirements.txt`** – Python dependencies for the FastAPI app
- **`backend/server.py`** – mounts `frontend/build` at `/` when that folder exists (Vercel build output)

## Local development

- **Backend:** `cd backend && pip install -r requirements.txt && uvicorn server:app --reload`
- **Frontend:** `cd frontend && yarn install && yarn start`  
  Set `REACT_APP_BACKEND_URL=http://localhost:8000` in `frontend/.env` so the app talks to the local API.
