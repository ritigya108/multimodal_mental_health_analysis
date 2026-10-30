# EATD-Corpus Dataset Guide

## What is the EATD-Corpus?

The **EATD-Corpus** (Emotional Audio-Textual Depression) was introduced in:

> Shen, Y., Yang, H., & Lin, L. (2022).  
> *Automatic Depression Detection: An Emotional Audio-Textual Corpus and a GRU/BiLSTM-Based Model.*  
> ICASSP 2022. [https://arxiv.org/abs/2202.08210](https://arxiv.org/abs/2202.08210)

It contains:
- **~162 participants**
- **Audio recordings** of responses to three emotional questions (positive, neutral, negative)
- **Text transcripts** of those responses
- **Labels** derived from the SDS (Self-Rating Depression Scale): binary threshold at SDS raw score ≥ 53
- **Class imbalance**: approximately 78% non-depressed, 22% depressed

---

## How to request access

The dataset is **not publicly downloadable**. You must contact the authors:

1. Read the paper at [https://arxiv.org/abs/2202.08210](https://arxiv.org/abs/2202.08210)
2. Email the corresponding author (contact details in the paper) with:
   - Your name, institution, and role
   - A brief statement of research purpose
   - Agreement to the data-use terms (see below)
3. Alternatively, check the GitHub repository linked in the paper for any updated access instructions.

---

## License and redistribution

- The dataset is provided for **academic research only**.
- **Do not redistribute** the audio files, transcripts, or any derived features.
- This repository's `.gitignore` blocks audio files (`*.wav`, `*.mp3`, `*.m4a`, etc.) and the `data/` directory to prevent accidental commits.
- Model checkpoints (`.pt`, `.pth`) are also blocked — they may embed participant-derived features.

---

## Expected folder layout after download

```
ICASSP2022-Depression/
├── train/
│   ├── t_1/
│   │   ├── +_out.wav          # positive-question audio
│   │   ├── 0_out.wav          # neutral-question audio
│   │   ├── -_out.wav          # negative-question audio
│   │   ├── +_out.txt          # positive transcript
│   │   ├── 0_out.txt          # neutral transcript
│   │   └── -_out.txt          # negative transcript
│   └── ...
└── val/
    ├── v_1/
    └── ...
```

The SDS labels are stored in `train_labels.csv` and `val_labels.csv` (or equivalent CSV files provided with the dataset).

---

## Preprocessing steps

Run the EATD adapter to convert the raw corpus to the processed format expected by the training pipeline:

```bash
cd backend
python eatd_adapter.py \
    --eatd_root /path/to/ICASSP2022-Depression \
    --output_dir data/eatd_processed
```

This script:
1. Concatenates the three audio files per participant
2. Extracts MFCC + prosodic features → `data/eatd_processed/audio_features/<id>.npy`
3. Merges the three text files → `data/eatd_processed/text_features/<id>.csv`
4. Maps SDS scores to binary labels and writes label CSVs in AVEC2017 format

After preprocessing, train with:

```bash
python train_cpu_fast.py \
    --data_root data/eatd_processed \
    --processed_dir data/eatd_processed \
    --epochs 30
```

---

## Citation

If you use the EATD-Corpus in your work, please cite:

```bibtex
@inproceedings{shen2022automatic,
  title     = {Automatic Depression Detection: An Emotional Audio-Textual Corpus and a {GRU}/{BiLSTM}-Based Model},
  author    = {Shen, Yiheng and Yang, Hebin and Lin, Linlin},
  booktitle = {ICASSP 2022 -- IEEE International Conference on Acoustics, Speech and Signal Processing},
  pages     = {6247--6251},
  year      = {2022},
  doi       = {10.1109/ICASSP43922.2022.9747870}
}
```
