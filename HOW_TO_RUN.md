# 🚀 HOW TO RUN — MindCare AI Multimodal Mental Health Analysis

> **You do NOT need the DAIC-WOZ dataset to run the project right now.**
> Everything works with the included synthetic data.
> See [`DATASET_SWAP_GUIDE.md`](DATASET_SWAP_GUIDE.md) for what changes when you get it.

---

## Quick Start (5 minutes)

### 1. Install Python dependencies

```bash
cd multimodal_mental_health_analysis/backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
pip install -r requirements_multimodal.txt
```

### 2. Start the backend API

```bash
# (venv must be active)
cd multimodal_mental_health_analysis/backend
python main.py
```

Backend runs at **http://localhost:8000**
API docs at **http://localhost:8000/docs** (FastAPI Swagger UI)

### 3a. Run the Streamlit app (recommended)

```bash
cd multimodal_mental_health_analysis/streamlit-app
pip install streamlit plotly requests
streamlit run Home.py
```

Opens at **http://localhost:8501**

### 3b. Run the React frontend (alternative)

```bash
cd multimodal_mental_health_analysis/frontend
npm install
npm start
```

Opens at **http://localhost:3000**

---

## Running the ML Pipeline (no real dataset needed)

The full training + evaluation pipeline works right now using **synthetic DAIC-WOZ data**
(already generated in `backend/data/synthetic_daic/`).

```bash
cd multimodal_mental_health_analysis
python run_pipeline.py --mode synthetic
```

This will:
1. Generate synthetic participant data (if not already done)
2. Preprocess features (audio MFCCs, text tokens, facial AU sequences)
3. Train the multimodal model (AudioCNN + BERT + BiLSTM + Attention Fusion)
4. Evaluate and print metrics to the console
5. Save checkpoints to `backend/checkpoints/synthetic/best.pt`

For a faster smoke-test (fewer participants):

```bash
python run_pipeline.py --mode synthetic --quick --epochs 5
```

---

## Project Pages

| Page | URL (Streamlit) | Description |
|------|----------------|-------------|
| Dashboard | http://localhost:8501 | Overview & mood trend |
| Mood Tracker | http://localhost:8501/Mood_Tracker | Log daily mood 1–10 |
| Journal | http://localhost:8501/Journal | Write + sentiment-analyse entries |
| AI Chat | http://localhost:8501/AI_Chat | Mental health chatbot |
| Resources | http://localhost:8501/Resources | Helplines, articles, exercises |
| Profile | http://localhost:8501/Profile | User settings |
| **Multimodal Analysis** | http://localhost:8501/Multimodal_Analysis | 🆕 Full AI analysis (text/audio/video) |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/health` | Health check |
| `POST` | `/api/mood/log` | Log a mood entry |
| `GET`  | `/api/mood/history/{user_id}` | Mood history |
| `POST` | `/api/journal/entry` | Create journal entry |
| `POST` | `/api/analyze/sentiment` | Text sentiment analysis |
| `GET`  | `/api/analyze/risk/{user_id}` | Risk assessment |
| `POST` | `/api/chat` | Chatbot |
| **`POST`** | **`/api/multimodal/analyze`** | 🆕 Full multimodal analysis (form upload) |
| **`POST`** | **`/api/multimodal/analyze/text`** | 🆕 Text-only JSON analysis |

### Test the multimodal endpoint directly

```bash
# Text-only (JSON body)
curl -X POST http://localhost:8000/api/multimodal/analyze/text \
     -H "Content-Type: application/json" \
     -d '{"text": "I have been feeling very sad and hopeless lately."}'

# With audio file
curl -X POST http://localhost:8000/api/multimodal/analyze \
     -F "text=I feel empty and exhausted all the time" \
     -F "audio_file=@path/to/audio.wav"
```

---

## Current Model Status

| Mode | Checkpoint location | Status |
|------|-------------------|--------|
| Synthetic | `backend/checkpoints/synthetic/best.pt` | ✅ Trained (included) |
| DAIC-WOZ | `backend/checkpoints/daic/best.pt` | ⏳ Awaiting dataset access |
| EATD-Corpus | `backend/checkpoints/eatd/best.pt` | ⏳ Optional free alternative |

The API automatically uses the best available checkpoint. If no checkpoint loads
(e.g. incompatible architecture after an upgrade), it falls back to the
**linguistic heuristic analyser** which requires zero extra dependencies.

---

## When You Get the DAIC-WOZ Dataset

See [`DATASET_SWAP_GUIDE.md`](DATASET_SWAP_GUIDE.md) — it's only 2 lines of config to change.

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: fastapi` | `pip install -r backend/requirements.txt` |
| `ModuleNotFoundError: streamlit` | `pip install streamlit plotly requests` |
| Backend port 8000 already in use | `python main.py` auto-reloads; kill the old process first |
| CORS error in browser | Backend must be running on port 8000 (it adds the React/Streamlit origins automatically) |
| `transformers` slow first run | BERT tokenizer downloads on first use (~400 MB). It is cached after that. |

---

*Made with Bob*
