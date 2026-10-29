# MindCare — Multimodal Mental Health Analysis

Clinical-grade multimodal depression screening using CNN, LSTM, and BiLSTM with late fusion on text, audio, and video signals.

> **Disclaimer:** This tool provides screening support only and is not a medical diagnosis. Results must be interpreted by a qualified healthcare professional.

---

## Features

### Core screening
- **Multimodal assessment** — text, voice, video, or combined input via a step-by-step tabbed form
- **Late-fusion CNN/LSTM/BiLSTM model** — trained on EATD-Corpus / synthetic DAIC-WOZ style data
- **Heuristic fallback** — runs without a model checkpoint; clearly flagged as demo mode
- **PHQ-8 questionnaire** — standard 0–3 scale, score + severity band, agreement check vs. model

### Reports and explainability
- **Per-assessment report** — risk level, confidence, modality contributions, key findings
- **Word-level highlighting** — negative/positive lexical indicators in transcript (toggleable)
- **Audio cue summary** — speech rate, pause ratio, pitch variability, energy (when audio provided)
- **PDF-style text export** — downloadable report per assessment

### Dashboard
- 4-card KPI row: risk level, model confidence, assessment count, change since last
- Segmented risk meter (Low / Moderate / Elevated / High)
- Modality contribution bars (Text / Audio / Video) with per-modality confidence
- Recent assessments table with pagination (5 rows), date, input type, risk badge, report link
- Loading skeletons, empty states, error states

### Safety
- **Crisis banner** — shown when risk is High or Critical; calm, non-alarming tone
- **Persistent footer** — configurable crisis helpline on every page (default: India Tele-MANAS 14416)
- **Crisis keyword detection** in chatbot responses

### Privacy and consent
- **First-use consent modal** — explains what is recorded and processed
- **Settings page** — "Delete all my data" (hard delete), consent withdrawal, data retention note
- Audio/video files deleted after feature extraction by default

### Model transparency
- **Model Performance page** — Accuracy, Precision, Recall, F1, ROC-AUC table + confusion matrix grid
- Metrics loaded from `backend/model_metrics.json` — update with your real training results

---

## API Endpoints (v2)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/config/helpline` | Crisis helpline config |
| POST | `/api/assess/multimodal` | **Primary** multimodal assessment (text + optional audio/video) |
| GET | `/api/assessments/{user_id}` | Assessment history (paginated) |
| DELETE | `/api/users/{user_id}/data` | Hard-delete all user data |
| POST | `/api/phq8/score` | Score a PHQ-8 questionnaire (8 answers 0–3) |
| GET | `/api/phq8/history/{user_id}` | PHQ-8 history |
| GET | `/api/model/metrics` | Model performance metrics from JSON |
| POST | `/api/journal/entry` | Create journal entry |
| GET | `/api/journal/entries/{user_id}` | Journal entries |
| POST | `/api/chat` | AI chatbot |
| POST | `/api/users/register` | Register user |
| GET | `/api/users/{user_id}` | User profile |
| POST | `/api/multimodal/analyze` | Legacy alias → `/api/assess/multimodal` |
| POST | `/api/multimodal/analyze/text` | Text-only JSON shortcut |

**Removed (v1 → v2):**
- `POST /api/mood/log` — Mood Tracker removed
- `GET /api/mood/history/{user_id}` — Mood Tracker removed
- `GET /api/recommendations/{user_id}` — inline in assessment result
- `GET /api/analyze/risk/{user_id}` — replaced by `/api/assess/multimodal`

---

## Project Structure

```
multimodal_mental_health_analysis/
├── backend/
│   ├── main.py                  # FastAPI app + all endpoints
│   ├── app_config.py            # Helpline, file size limits (edit here)
│   ├── model_metrics.json       # Update with your real training metrics
│   ├── ai_analyzer.py           # VADER/TextBlob/Transformers sentiment
│   ├── multimodal_model.py      # CNN/LSTM/BiLSTM model definition
│   ├── train.py / train_cpu_fast.py  # Training scripts
│   ├── tests/
│   │   ├── test_phq8.py         # 17 PHQ-8 unit tests
│   │   └── test_multimodal.py   # 12 endpoint/heuristic tests
│   ├── checkpoints/             # Model checkpoints (eatd_fast > eatd > synthetic)
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/src/
│   ├── App.js                   # Routes + theme
│   ├── components/
│   │   ├── Navigation.js        # Collapsible sidebar, user menu
│   │   ├── CrisisFooter.js      # Persistent helpline footer
│   │   ├── CrisisBanner.js      # High/Critical risk banner
│   │   └── ConsentModal.js      # First-use consent dialog
│   ├── pages/
│   │   ├── Dashboard.js         # Clinical dashboard (no charts)
│   │   ├── Assessment.js        # Multimodal assessment + recording
│   │   ├── ReportDetail.js      # Per-report explainability
│   │   ├── PHQ8.js              # PHQ-8 questionnaire
│   │   ├── ModelPerformance.js  # Metrics table + confusion matrix
│   │   ├── Settings.js          # Privacy + delete data
│   │   ├── Journal.js
│   │   ├── ChatBot.js
│   │   └── Profile.js
│   └── services/api.js          # Axios + all API methods
│
└── streamlit-app/
    ├── Home.py                  # Overview dashboard
    └── pages/
        ├── 1_Assessment.py      # Assessment (mirrors React page)
        ├── 2_PHQ8.py            # PHQ-8 questionnaire
        ├── 3_AI_Chat.py
        ├── 2_Journal.py
        └── 5_Profile.py
```

---

## Setup

### Backend

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py
# → http://localhost:8000
# → API docs: http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm start
# → http://localhost:3000
```

### Streamlit demo

```bash
cd streamlit-app
pip install streamlit requests plotly
streamlit run Home.py
```

### Run tests

```bash
cd backend
python -m pytest tests/ -v
# 29 tests, all pass
```

---

## Configuration

### Crisis helpline
Edit [`backend/app_config.py`](backend/app_config.py):
```python
CRISIS_HELPLINE_NUMBER = "14416"
CRISIS_HELPLINE_NAME   = "Tele-MANAS"
```
The frontend and Streamlit app read this from `/api/config/helpline` at runtime.

### Model metrics
Edit [`backend/model_metrics.json`](backend/model_metrics.json) with your real training results. The Model Performance page loads these at request time.

### Environment variables
See [`.env.example`](backend/.env.example).

---

## Training

```bash
# Fast CPU training (recommended for demo)
cd backend
python train_cpu_fast.py

# Full BERT-based training (requires GPU)
python run_pipeline.py --mode eatd   # with EATD-Corpus
python run_pipeline.py --mode daic   # with real DAIC-WOZ
```

---

## Screenshots

> _(Add screenshots to `docs/screenshots/` after first run)_
> - `docs/screenshots/dashboard.png`
> - `docs/screenshots/assessment.png`
> - `docs/screenshots/phq8.png`
> - `docs/screenshots/report.png`
> - `docs/screenshots/model_performance.png`

---

## ML Architecture

- **Text branch**: TF-IDF (fast) or BERT encoder → 1D CNN
- **Audio branch**: Mel-spectrogram → 2D CNN → LSTM
- **Facial/Video branch**: AU features → BiLSTM
- **Fusion**: Late-fusion MLP combining all three branch embeddings
- **Dataset**: EATD-Corpus / synthetic DAIC-WOZ style
- **Task**: Binary classification (depressed / non-depressed)
- **Metrics**: See `backend/model_metrics.json`

---

*Made with IBM Bob*
