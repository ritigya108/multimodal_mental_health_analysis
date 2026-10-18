# 🚀 MindCare AI — Deployment Guide

Complete instructions for deploying all three services:

| Service | URL | Stack |
|---------|-----|-------|
| **React Frontend** | `http://localhost:3000` | React 18 + Nginx |
| **FastAPI Backend** | `http://localhost:8000` | FastAPI + Uvicorn |
| **Streamlit Demo** | `http://localhost:8501` | Streamlit |

---

## 🐳 Option 1 — Docker Compose (Recommended for local + VPS)

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) ≥ 24
- [Docker Compose](https://docs.docker.com/compose/) ≥ 2 (bundled with Docker Desktop)

### Step 1 — Configure environment

```bash
cd multimodal_mental_health_analysis

# Copy and edit the backend .env file
cp backend/.env.example backend/.env
```

Edit `backend/.env` with your values:
```env
SECRET_KEY=your_super_secret_key_change_this
DATABASE_URL=           # leave blank to use in-memory SQLite
OPENAI_API_KEY=         # optional — only needed for GPT chatbot
ENVIRONMENT=production
```

### Step 2 — Build and run

```bash
# First run (builds all images — takes 3-5 minutes)
docker compose up --build

# Subsequent runs
docker compose up -d

# View logs
docker compose logs -f

# Stop everything
docker compose down
```

### Step 3 — Access the app

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Streamlit | http://localhost:8501 |

> **Tip:** The Nginx frontend proxies all `/api/*` calls to the backend, so the React app
> works from a single domain in production. No CORS setup needed.

### Updating after code changes

```bash
# Rebuild only the changed service
docker compose up --build backend
docker compose up --build frontend
docker compose up --build streamlit
```

### Persisting model checkpoints

Model checkpoints are stored in a named Docker volume (`mindcare_checkpoints`).  
They survive container restarts and rebuilds automatically.

```bash
# Inspect the volume
docker volume inspect mindcare_checkpoints

# Backup checkpoints
docker run --rm -v mindcare_checkpoints:/data -v $(pwd):/backup \
    alpine tar czf /backup/checkpoints_backup.tar.gz /data
```

---

## ☁️ Option 2 — Streamlit Cloud (Free, no server needed)

Deploy the Streamlit ML demo as a **permanent public URL** in 5 minutes.

### Step 1 — Push to GitHub

```bash
cd multimodal_mental_health_analysis
git add .
git commit -m "Add Docker deployment files"
git push origin main
```

### Step 2 — Deploy on Streamlit Cloud

1. Go to **https://share.streamlit.io/**
2. Sign in with GitHub
3. Click **"New app"**
4. Fill in:
   - **Repository**: `your_username/multimodal_mental_health_analysis`
   - **Branch**: `main`
   - **Main file path**: `streamlit-app/Home.py`
5. Click **"Deploy!"**

Wait 2-3 minutes → you'll get a URL like:
```
https://mindcare-yourname.streamlit.app
```

### Step 3 — Add secrets (optional)

If you deploy the FastAPI backend separately (e.g. Railway, Render, Fly.io), tell
Streamlit where to find it:

1. In Streamlit Cloud → **App settings** → **Secrets**
2. Paste:
   ```toml
   BACKEND_URL = "https://your-api.railway.app"
   ```

Without this secret, the Streamlit app runs in **standalone mode** (linguistic
heuristic analysis — no backend needed).

---

## 🚂 Option 3 — Deploy Backend to Railway / Render / Fly.io

### Railway (easiest)

```bash
npm install -g @railway/cli
cd multimodal_mental_health_analysis/backend
railway login
railway init
railway up
```

Set env variables in Railway dashboard:
- `SECRET_KEY`
- `ENVIRONMENT=production`

Railway gives you a URL like `https://mindcare-backend.up.railway.app`.  
Add this to your Streamlit Cloud secrets as `BACKEND_URL`.

### Render

1. Go to https://render.com → **New Web Service**
2. Connect your GitHub repo
3. Settings:
   - **Root directory**: `backend`
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables in the Render dashboard

### Fly.io

```bash
cd multimodal_mental_health_analysis/backend
flyctl launch --dockerfile Dockerfile
flyctl deploy
```

---

## 🏗️ Option 4 — VPS / Cloud VM (Ubuntu 22.04)

For a full production stack on a DigitalOcean / AWS / GCP VM:

### Install Docker

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Log out and back in
```

### Clone and run

```bash
git clone https://github.com/your_username/multimodal_mental_health_analysis.git
cd multimodal_mental_health_analysis
cp backend/.env.example backend/.env
nano backend/.env   # fill in secrets
docker compose up -d --build
```

### Set up Nginx reverse proxy (optional — for custom domain)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
    }
    location /api/ {
        proxy_pass http://localhost:8000;
    }
    location /streamlit/ {
        proxy_pass http://localhost:8501;
    }
}
```

### Enable HTTPS with Certbot

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

---

## 🔧 Troubleshooting

### Docker

| Issue | Fix |
|-------|-----|
| `permission denied` on Docker socket | Run `sudo usermod -aG docker $USER` and re-login |
| Port 3000 already in use | Change `"3000:80"` to `"3001:80"` in `docker-compose.yml` |
| Backend not healthy after 20s | Check logs: `docker compose logs backend` |
| `ENOSPC` build error | Run `docker system prune -a` to free space |

### Streamlit Cloud

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError` | Check `streamlit-app/requirements.txt` |
| App crashes on start | Check app logs in Streamlit Cloud dashboard |
| Backend connection refused | Add `BACKEND_URL` to Streamlit Cloud secrets |
| Audio upload fails | Ensure `libsndfile1` is in `packages.txt` ✅ (already done) |

---

## 📊 Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                   Browser / Client                        │
└─────────────────┬──────────────────────┬─────────────────┘
                  │ :3000                 │ :8501
    ┌─────────────▼─────────────┐  ┌────▼──────────────────┐
    │   React Frontend (Nginx)  │  │  Streamlit Demo App    │
    │   /api/* → backend:8000   │  │  (optional backend)    │
    └─────────────┬─────────────┘  └───────────────────────┘
                  │ internal
    ┌─────────────▼─────────────┐
    │   FastAPI Backend :8000   │
    │   + Multimodal ML models  │
    └─────────────┬─────────────┘
                  │
    ┌─────────────▼─────────────┐
    │   Named Docker Volumes    │
    │   checkpoints / data      │
    └───────────────────────────┘
```

---

## 📝 Quick Reference

```bash
# Start everything
docker compose up -d --build

# Stop everything  
docker compose down

# View all logs
docker compose logs -f

# Restart single service
docker compose restart backend

# Shell into backend container
docker compose exec backend bash

# Check container health
docker compose ps
```

---

> ⚠️ **Disclaimer:** This application is a support tool and NOT a replacement for
> professional mental health care. Always consult a qualified mental health professional.
>
> 🚨 **Emergency (India):** KIRAN 1800-599-0019 · iCall 9152987821 · Vandrevala 1860-2662-345

---

*Made with ❤️ by Bob*
