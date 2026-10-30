# Deployment

## Option 1 — Docker Compose (recommended)

```bash
# Build and start all services
docker-compose up --build

# Backend:   http://localhost:8000
# Frontend:  http://localhost:3000
# Streamlit: http://localhost:8501
```

Environment variables are read from a `.env` file in the repo root.  
Copy `.env.example` to `.env` and adjust before building.

---

## Option 2 — Streamlit Cloud (free tier)

1. Push the repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and click **New app**.
3. Set:
   - Repository: `ritigya108/multimodal_mental_health_analysis`
   - Branch: `main`
   - Main file path: `streamlit-app/Home.py`
4. In **Advanced settings → Secrets**, add:
   ```toml
   BACKEND_URL = "https://your-backend-url"
   ```
5. Click **Deploy**.

---

## Option 3 — Backend on Railway / Render / Fly.io

1. Create a new service pointing to the `backend/` directory.
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variable `FRONTEND_URL` pointing to your deployed frontend URL.

---

## Option 4 — VPS with Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api {
        proxy_pass http://127.0.0.1:8000;
    }

    location / {
        root /var/www/frontend/build;
        try_files $uri /index.html;
    }
}
```

Build the React app first: `cd frontend && npm run build`

---

## Environment variables

See `.env.example` for the full list. Key variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `FRONTEND_URL` | `http://localhost:3000` | CORS allow-origin for the backend |
| `CRISIS_HELPLINE_NUMBER` | `14416` | Overrides `app_config.py` at runtime |
| `PORT` | `8000` | Backend port (used by cloud hosts) |
