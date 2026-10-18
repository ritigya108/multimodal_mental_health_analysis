# 🔄 DATASET SWAP GUIDE — Switching from Synthetic to Real DAIC-WOZ

> **When your DAIC-WOZ access email arrives**, follow these steps in order.
> Nothing else in the codebase needs to change.

---

## Step 0 — Prerequisites

Make sure these are already installed (they were set up during the original install):

```bash
pip install torch torchvision torchaudio transformers librosa soundfile
pip install -r backend/requirements.txt
pip install -r backend/requirements_multimodal.txt
```

---

## Step 1 — Download DAIC-WOZ

1. Go to [https://dcapswoz.ict.usc.edu/](https://dcapswoz.ict.usc.edu/)
2. Sign and submit the **Data Use Agreement**
3. Wait for the download link (1–3 business days)
4. Download and extract to a folder, e.g. `C:\data\daic-woz\`

Your folder should look like this:

```
C:\data\daic-woz\
├── train_split_Depression_AVEC2017.csv
├── dev_split_Depression_AVEC2017.csv
├── test_split_Depression_AVEC2017.csv
├── train\
│   ├── 300_P\
│   │   ├── 300_AUDIO.wav
│   │   ├── 300_CLNF_features.txt   ← OpenFace facial AUs
│   │   └── 300_TRANSCRIPT.csv
│   ├── 301_P\
│   ...
├── dev\
│   └── ...
└── test\
    └── ...
```

---

## Step 2 — Run the Pipeline (One Command)

```bash
# From the project root:
python run_pipeline.py --mode daic --daic_root C:\data\daic-woz

# On macOS / Linux:
python run_pipeline.py --mode daic --daic_root /data/daic-woz
```

This single command does everything automatically:
1. **Cleans + preprocesses** all three splits (train / dev / test)
2. **Trains** the multimodal model (AudioCNN + BERT + FacialAU-BiLSTM + Attention Fusion)
3. **Evaluates** on the dev split and prints accuracy, F1, RMSE, AUC
4. **Saves checkpoints** to `backend/checkpoints/daic/best.pt`

---

## Step 3 — Update `config.py` (optional but recommended)

Open [`backend/config.py`](backend/config.py) and change **only these two lines**:

```python
# BEFORE (synthetic mode)
DATASET_MODE = "synthetic"
DAIC_ROOT    = None

# AFTER (real DAIC-WOZ)
DATASET_MODE = "daic"
DAIC_ROOT    = Path("C:/data/daic-woz")   # ← your actual path
```

This makes `config.py` the single source of truth for all scripts.

---

## Step 4 — Update the API to use the new checkpoint

Open [`backend/main.py`](backend/main.py) and change **one line** in the
`MODEL_CHECKPOINT` constant near line 215:

```python
# BEFORE (synthetic checkpoint)
MODEL_CHECKPOINT = Path(__file__).parent / "checkpoints" / "synthetic" / "best.pt"

# AFTER (real DAIC-WOZ checkpoint — trained in Step 2)
MODEL_CHECKPOINT = Path(__file__).parent / "checkpoints" / "daic" / "best.pt"
```

Restart the backend: `python backend/main.py`

The Streamlit page and the React frontend **need zero changes** — they both call
the same `/api/multimodal/analyze` endpoint which now returns neural predictions.

---

## Step 5 — Verify (optional)

```bash
# Quick smoke-test — should print neural model results
python backend/evaluate.py \
  --checkpoint backend/checkpoints/daic/best.pt \
  --daic_root  C:\data\daic-woz \
  --processed_dir C:\data\daic-woz\processed \
  --split dev \
  --show_weights
```

Expected output (ballpark):
```
  accuracy             : 0.84+
  f1                   : 0.76+
  auc                  : 0.88+
  Average modality attention weights:
    audio   : ~0.33
    text    : ~0.40
    facial  : ~0.27
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `FileNotFoundError: Label file not found` | Check `DAIC_ROOT` points to the folder containing `train_split_Depression_AVEC2017.csv` |
| `KeyError: PHQ8_Binary` | Re-download the label CSV — some mirrors have different column names. The official USC download is correct. |
| `CUDA out of memory` | Reduce batch size: add `--batch_size 4` to `run_pipeline.py` |
| `transformers` model download hangs | Set `HF_HUB_OFFLINE=1` after first download, or use `--freeze_bert 1` (default) to skip fine-tuning |
| OpenFace AU columns missing from CSV | The `clean_daic_dataset.py` script handles this — missing AU columns are zero-padded automatically |
| `ModuleNotFoundError: librosa` | `pip install librosa soundfile` |

---

## Summary — Files Changed When You Get the Dataset

| File | What to change |
|------|---------------|
| `backend/config.py` | `DATASET_MODE = "daic"`, `DAIC_ROOT = Path(...)` |
| `backend/main.py` | `MODEL_CHECKPOINT = .../checkpoints/daic/best.pt` |
| Everything else | **No changes needed** |

---

## What Does NOT Need to Change

- ✅ `backend/multimodal_model.py` — architecture is dataset-agnostic
- ✅ `backend/train.py` — already handles DAIC-WOZ natively
- ✅ `backend/dataset.py` — already reads DAIC-WOZ label CSVs
- ✅ `backend/evaluate.py` — already computes AVEC standard metrics
- ✅ `frontend/src/pages/MultimodalAnalysis.js` — calls the same API
- ✅ `streamlit-app/pages/6_Multimodal_Analysis.py` — calls the same API
- ✅ All other frontend pages — completely unaffected

---

*Made with Bob*
