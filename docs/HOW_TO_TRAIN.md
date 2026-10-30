# How to Train

## Prerequisites

- Python 3.9+, PyTorch 2.x
- GPU optional but recommended for the BERT-based full model
- EATD-Corpus (see [EATD_DATASET_GUIDE.md](EATD_DATASET_GUIDE.md))

---

## Mode 1 — Synthetic data (no dataset needed)

Generates a structurally-compatible synthetic dataset and trains immediately.

```bash
# From repo root
python run_pipeline.py --mode synthetic

# Options
python run_pipeline.py --mode synthetic \
    --epochs 30 \
    --batch_size 8 \
    --lr 2e-4 \
    --task classification \
    --output_dir ./backend/checkpoints
```

---

## Mode 2 — EATD-Corpus (real training)

```bash
# Step 1: convert EATD to the processed format
cd backend
python eatd_adapter.py \
    --eatd_root /path/to/ICASSP2022-Depression \
    --output_dir data/eatd_processed

# Step 2: fast CPU training (TF-IDF text encoder)
python train_cpu_fast.py \
    --data_root data/eatd_processed \
    --processed_dir data/eatd_processed \
    --epochs 30 --batch_size 8

# Step 3: full BERT-based training (GPU recommended)
python train.py \
    --data_root data/eatd_processed \
    --processed_dir data/eatd_processed \
    --epochs 30 --batch_size 8 --lr 2e-4 \
    --freeze_bert 1 \
    --output_dir checkpoints/eatd
```

---

## Evaluate a checkpoint

```bash
python run_pipeline.py \
    --mode evaluate \
    --checkpoint backend/checkpoints/eatd_fast/best.pt
```

---

## Checkpoint priority

The backend loads checkpoints in this order:

1. `backend/checkpoints/eatd_fast/best.pt`
2. `backend/checkpoints/eatd/best.pt`
3. `backend/checkpoints/synthetic/best.pt`

If none is found, it falls back to the linguistic heuristic analyser.

---

## Update metrics after training

Copy your results to both:
- `ml/results/metrics.json` (canonical, tracked in git)
- `backend/model_metrics.json` (served by `/api/model/metrics`)

Both files have matching JSON schemas with `"_note": "TODO"` markers
indicating values that need replacement.
