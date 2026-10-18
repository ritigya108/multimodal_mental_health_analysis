# 📦 Dataset Guide — How to Get Data for Your Project

## The Problem: DAIC-WOZ is Gated

DAIC-WOZ requires signing a Data Use Agreement with USC (1–3 business days).
While you wait (or if you cannot get it), you have **two working alternatives right now**.

---

## ⚡ Option A — Run RIGHT NOW (No Download Needed)

Synthetic DAIC-WOZ data is already built into this project.
The generator creates audio, transcripts, and facial features that are
**structurally identical** to the real dataset. The full training pipeline runs on it.

### One command to run the pipeline end-to-end:

Open PowerShell, go to the backend folder, activate your venv, then:

```powershell
cd multimodal_mental_health_analysis\backend

# Create virtual env (if not done yet)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Step 1 — Generate synthetic dataset (~1 minute)
python generate_synthetic_daic.py --output_dir .\data\synthetic_daic

# Step 2 — Preprocess it
python clean_daic_dataset.py --raw_dir .\data\synthetic_daic --output_dir .\data\synthetic_daic\processed --split train
python clean_daic_dataset.py --raw_dir .\data\synthetic_daic --output_dir .\data\synthetic_daic\processed --split dev

# Step 3 — Train (5 epochs for a quick demo)
python train.py `
    --daic_root     .\data\synthetic_daic `
    --processed_dir .\data\synthetic_daic\processed `
    --task          classification `
    --epochs        5 `
    --batch_size    4 `
    --output_dir    .\checkpoints\synthetic `
    --no_cuda

# Step 4 — Evaluate
python evaluate.py `
    --checkpoint    .\checkpoints\synthetic\best.pt `
    --daic_root     .\data\synthetic_daic `
    --processed_dir .\data\synthetic_daic\processed `
    --split         dev
```

✅ **This works today. Your model trains and generates real metric outputs.**
⚠️ Accuracy numbers from synthetic data are for demo only — not for your report results table.

---

## 🆓 Option B — EATD-Corpus (Best Free Real Dataset)

Real depression data. 162 real participants. Real SDS depression scores.
Free download. No approval needed.

### Step 1 — Download the dataset

1. Open this link in your browser:
   **https://1drv.ms/u/s!AsGVGqImbOwYhHUHcodFC3xmKZKK?e=mCT5oN**
2. Password: **Ymj26Uv5**
3. Download and extract the ZIP file
4. You will get a folder with `train/` and `validation/` subfolders

> **What's inside:** Each participant folder has `positive.wav`, `negative.wav`,
> `neutral.wav`, text transcripts, and a `label.txt` with their SDS (depression) score.

### Step 2 — Convert to pipeline format

```powershell
cd multimodal_mental_health_analysis\backend
.\venv\Scripts\Activate.ps1

# Replace C:\Users\HP\EATD-Corpus with your actual extracted folder path
python eatd_adapter.py `
    --eatd_root  C:\Users\HP\Downloads\EATD-Corpus `
    --output_dir .\data\eatd_processed
```

### Step 3 — Train on real data

```powershell
python train.py `
    --daic_root     .\data\eatd_processed `
    --processed_dir .\data\eatd_processed `
    --task          classification `
    --epochs        30 `
    --batch_size    8 `
    --output_dir    .\checkpoints\eatd `
    --no_cuda
```

### Step 4 — Evaluate

```powershell
python evaluate.py `
    --checkpoint    .\checkpoints\eatd\best.pt `
    --daic_root     .\data\eatd_processed `
    --processed_dir .\data\eatd_processed `
    --split         dev
```

✅ **These results are real and can go in your report/presentation.**

> **Note for presentation:** Say "We used the EATD-Corpus for our experiments,
> which provides real annotated audio and text data for depression detection."

---

## 🔑 Option C — Request DAIC-WOZ (Official, Takes 1–3 Days)

### Step 1 — Fill the form

Go to: **https://dcapswoz.ict.usc.edu/**
Click **"Request Database Access"** and fill in:

| Field | What to write |
|-------|--------------|
| Name | Your full name |
| Affiliation | Your college/university name |
| Email | Your college email (preferred) |
| Research Purpose | "Depression detection using multimodal deep learning for academic final year project" |
| Intended Use | "Training and evaluating CNN + BiLSTM models for automated depression screening" |

### Step 2 — Wait for email (1–3 business days)

Check your spam folder. Reply email comes from `dcapswoz@ict.usc.edu`.

### Step 3 — Download and set up

Once you get the download link:

```powershell
# After extracting the dataset to C:\Users\HP\DAIC-WOZ:
cd multimodal_mental_health_analysis\backend

python clean_daic_dataset.py `
    --raw_dir  C:\Users\HP\DAIC-WOZ `
    --output_dir .\data\daic_processed `
    --split train

python clean_daic_dataset.py `
    --raw_dir  C:\Users\HP\DAIC-WOZ `
    --output_dir .\data\daic_processed `
    --split dev

python train.py `
    --daic_root     .\data\daic_processed `
    --processed_dir .\data\daic_processed `
    --task          classification `
    --epochs        30 `
    --batch_size    8 `
    --output_dir    .\checkpoints\daic `
    --no_cuda
```

---

## 🎯 Recommended Plan Based on Your Timeline

| Situation | Use This |
|-----------|---------|
| Need to demo/run TODAY | Option A (Synthetic) |
| Want real results for report | Option B (EATD) |
| Have 3+ days before submission | Option C (DAIC-WOZ request) |
| Already have DAIC-WOZ | Option C setup above |

---

## 📝 What to Say in Your Report / Viva

### If using EATD-Corpus:
> "We trained and evaluated our multimodal model on the EATD-Corpus, a real
> depression dataset with 162 participants, labeled using the SDS (Self-Rating
> Depression Scale). The dataset includes audio recordings and text transcripts."

### If using DAIC-WOZ:
> "We used the DAIC-WOZ dataset, which contains 189 participants from clinical
> interviews, labeled with PHQ-8 scores. Access was obtained under a Data Use
> Agreement from the USC SAIL Laboratory."

### If using Synthetic for demo only:
> "For development and demonstration, we used a synthetic dataset that mirrors
> the structure of DAIC-WOZ. Final evaluation will be done on the real dataset
> once access is approved."

---

## ❓ Troubleshooting

**"pip install fails"**
```powershell
pip install --upgrade pip
pip install librosa soundfile numpy pandas torch --no-cache-dir
```

**"eatd_adapter.py: no participant folders found"**
Make sure you extracted the ZIP and are pointing to the folder
that contains `train/` and `validation/` subfolders, not the ZIP itself.

**"DAIC-WOZ email not received after 3 days"**
Send a follow-up email to: **dcapswoz@ict.usc.edu**
Subject: "Data Use Agreement Follow-up - [Your Name]"

**"train.py crashes with CUDA error"**
Add `--no_cuda` flag to the train command (runs on CPU).

---

> ⚠️ **Disclaimer:** All datasets must be used for research purposes only.
> Do not share or redistribute the data.
