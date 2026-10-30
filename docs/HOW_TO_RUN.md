# How to Run

## Prerequisites

| Tool | Minimum version |
|------|----------------|
| Python | 3.9 |
| Node.js | 18 |
| npm | 9 |
| Git | any |

---

## 1. Clone the repository

```bash
git clone https://github.com/ritigya108/multimodal_mental_health_analysis.git
cd multimodal_mental_health_analysis
```

---

## 2. Backend (FastAPI)

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt

cp ../.env.example .env   # edit if needed (helpline number, ports)
python main.py
```

Backend runs at **http://localhost:8000**  
Interactive API docs: **http://localhost:8000/docs**

---

## 3a. Streamlit demo app (quickest)

```bash
cd streamlit-app
pip install streamlit plotly requests
streamlit run Home.py
```

Opens at **http://localhost:8501**

---

## 3b. React frontend (full UI)

```bash
cd frontend
npm install
npm start
```

Opens at **http://localhost:3000**

---

## 4. Run ML training (no real dataset required)

The synthetic mode works out-of-the-box:

```bash
# From repo root
python run_pipeline.py --mode synthetic

# Quick smoke-test (5 epochs)
python run_pipeline.py --mode synthetic --quick --epochs 5
```

To train on the real EATD-Corpus, first follow [EATD_DATASET_GUIDE.md](EATD_DATASET_GUIDE.md), then:

```bash
python run_pipeline.py --mode eatd --eatd_root /path/to/ICASSP2022-Depression
```

Checkpoints are saved to `backend/checkpoints/`.

---

## 5. Run tests

```bash
cd backend
python -m pytest tests/ -v
```

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: fastapi` | Run `pip install -r backend/requirements.txt` |
| `ModuleNotFoundError: streamlit` | Run `pip install streamlit plotly requests` |
| Port 8000 already in use | Kill the existing process; `python main.py` does not auto-reload |
| CORS error in browser | Backend must be running on port 8000 |
| BERT tokenizer slow on first run | Downloads ~400 MB; cached afterwards |
