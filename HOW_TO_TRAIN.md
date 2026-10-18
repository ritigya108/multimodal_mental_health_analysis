# How to Train the Multimodal Depression Detection Model on DAIC-WOZ

This guide walks you through every step — from obtaining the dataset to running the final evaluation.

---

## 1. Prerequisites

- Python 3.9 or 3.10
- CUDA GPU strongly recommended (GTX 1080 / RTX 2060 or better)
- ~20 GB disk space for processed features
- ~150 GB disk space if you also keep the raw audio/video files

---

## 2. Install dependencies

```bash
cd multimodal_mental_health_analysis/backend
pip install -r requirements_multimodal.txt
```

---

## 3. Obtain the DAIC-WOZ dataset

DAIC-WOZ is **not publicly downloadable** — you must request access:

1. Go to **https://dcapswoz.ict.usc.edu/**
2. Click **"Request Database Access"**
3. Fill in your name, institutional email, and research purpose
4. Wait for the approval email (1–3 business days)
5. Download the dataset using the link they send you

After download, your folder should look like:

```
/data/daic-woz/
├── train_split_Depression_AVEC2017.csv
├── dev_split_Depression_AVEC2017.csv
├── test_split_Depression_AVEC2017.csv
├── train/
│   ├── 300_P/
│   │   ├── 300_AUDIO.wav
│   │   ├── 300_TRANSCRIPT.csv
│   │   └── 300_CLNF_features.txt
│   └── ...
├── dev/
│   └── ...
└── test/
    └── ...
```

---

## 4. Preprocess the dataset

Run the cleaning script for each split:

```bash
# Process training set
python clean_daic_dataset.py \
    --raw_dir  /data/daic-woz \
    --output_dir /data/daic-woz/processed \
    --split train

# Process dev set
python clean_daic_dataset.py \
    --raw_dir  /data/daic-woz \
    --output_dir /data/daic-woz/processed \
    --split dev

# Process test set
python clean_daic_dataset.py \
    --raw_dir  /data/daic-woz \
    --output_dir /data/daic-woz/processed \
    --split test
```

This creates:

```
/data/daic-woz/processed/
├── audio_features/      300.npy, 301.npy, ...
├── text_features/       300.csv, 301.csv, ...
├── facial_features/     300.csv, 301.csv, ...
├── processed_audio/     300.wav, 301.wav, ...
└── quality_report_train.json
```

---

## 5. Train — binary classification (PHQ-8 ≥ 10 = depressed)

```bash
python train.py \
    --daic_root     /data/daic-woz \
    --processed_dir /data/daic-woz/processed \
    --task          classification \
    --epochs        30 \
    --batch_size    8 \
    --lr            2e-4 \
    --embed_dim     256 \
    --dropout       0.3 \
    --freeze_bert   1 \
    --output_dir    ./checkpoints/classification
```

---

## 5b. Train — PHQ-8 score regression (0–24)

```bash
python train.py \
    --daic_root     /data/daic-woz \
    --processed_dir /data/daic-woz/processed \
    --task          regression \
    --epochs        40 \
    --batch_size    8 \
    --lr            1e-4 \
    --embed_dim     256 \
    --dropout       0.3 \
    --freeze_bert   1 \
    --output_dir    ./checkpoints/regression
```

> **Tip:** If you have raw `.wav` files and want on-the-fly mel-spectrogram loading  
> (instead of pre-saved `.npy`), add:  
> `--raw_audio_dir /data/daic-woz`

---

## 6. Evaluate the best checkpoint

```bash
# Classification
python evaluate.py \
    --checkpoint    ./checkpoints/classification/best.pt \
    --daic_root     /data/daic-woz \
    --processed_dir /data/daic-woz/processed \
    --split         dev \
    --output_json   ./checkpoints/classification/dev_metrics.json \
    --show_weights

# Regression
python evaluate.py \
    --checkpoint    ./checkpoints/regression/best.pt \
    --daic_root     /data/daic-woz \
    --processed_dir /data/daic-woz/processed \
    --split         dev \
    --output_json   ./checkpoints/regression/dev_metrics.json
```

---

## 7. Resume interrupted training

```bash
python train.py \
    --daic_root     /data/daic-woz \
    --processed_dir /data/daic-woz/processed \
    --task          classification \
    --output_dir    ./checkpoints/classification \
    --resume        ./checkpoints/classification/last.pt
```

---

## 8. Model architecture summary

```
Audio (.wav)          → AudioEncoder (CNN, 4 conv blocks)   → 256-d embedding
Text  (transcript)    → TextEncoder  (BERT-base + proj)     → 256-d embedding
Facial (OpenFace AUs) → FacialAUEncoder (BiLSTM 2-layer)    → 256-d embedding
                              ↓
                   CrossModalAttentionFusion
                   (learnable scalar weight per modality,
                    softmax-normalised, weighted sum + MLP)
                              ↓
              Classification head: Linear → 2 classes
              Regression head:     Linear → 1 scalar (clamped 0–24)
```

---

## 9. Expected results (AVEC 2017 baselines for reference)

| Model | Task | F1 | RMSE |
|---|---|---|---|
| Audio-only baseline | Classification | ~0.52 | — |
| Text-only baseline  | Classification | ~0.58 | — |
| Multimodal (this)   | Classification | **~0.65–0.72** | — |
| Audio-only baseline | Regression | — | ~6.0 |
| Multimodal (this)   | Regression | — | **~4.5–5.5** |

Actual results depend on preprocessing quality and whether BERT is fine-tuned.

---

## 10. Fine-tuning BERT (optional, for higher accuracy)

By default BERT weights are frozen except the last 2 transformer layers.  
To fully fine-tune BERT (requires more GPU memory and a lower LR):

```bash
python train.py \
    --freeze_bert 0 \
    --lr          5e-5 \
    --batch_size  4 \
    --epochs      20 \
    ...
```

---

## 11. New files added by this training pipeline

| File | Purpose |
|---|---|
| `backend/dataset.py` | DAIC-WOZ PyTorch Dataset + DataLoader factory |
| `backend/multimodal_model.py` | Full model: AudioCNN + BERT + AU-BiLSTM + Attention Fusion |
| `backend/train.py` | Training loop with class-weighted loss, cosine LR, checkpointing |
| `backend/evaluate.py` | Standalone evaluation with AVEC metrics + confusion matrix |
| `backend/clean_daic_dataset.py` | Data cleaning + feature extraction (pre-existing) |

---

## 12. Citation

If you use this code or DAIC-WOZ in a publication, please cite:

```bibtex
@inproceedings{gratch2014distress,
  title={The distress analysis interview corpus of human and computer interviews},
  author={Gratch, Jonathan and others},
  booktitle={LREC},
  pages={3123--3128},
  year={2014}
}
```

---

> ⚠️ DAIC-WOZ contains sensitive mental health data. Handle with care, follow your institution's IRB/ethics guidelines, and never redistribute the raw data.
