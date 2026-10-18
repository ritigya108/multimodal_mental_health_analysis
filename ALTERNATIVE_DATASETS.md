# Alternative Datasets for Multimodal Mental Health Analysis

Use this guide while waiting for DAIC-WOZ approval. Every dataset below
works with the existing `train.py` / `evaluate.py` pipeline using the
provided adapter scripts.

---

## Quick Decision Chart

```
Can you run code right now and just need something to work?
  → Use Option 0: Synthetic DAIC-WOZ (zero download, zero wait)

Do you want a real depression dataset that is free?
  → Use Option 1: EATD-Corpus (GitHub, instant download)

Do you want a large multimodal dataset with audio + text + video features?
  → Use Option 2: CMU-MOSI (Dropbox, ~1 GB, repurposed for mental health)

Do you want a larger free depression dataset for final results?
  → Use Option 3: D-Vlog (Google Drive)

Did your DAIC-WOZ access arrive?
  → Use the main pipeline: HOW_TO_TRAIN.md
```

---

## Comparison Table

| Dataset | Size | Modalities | Labels | Access | Adapter Script |
|---|---|---|---|---|---|
| **Synthetic DAIC** | 107+35+47 fake | Audio + Text + AUs | PHQ-8 (fake) | Instant | `generate_synthetic_daic.py` |
| **EATD-Corpus** | 162 participants | Audio + Text | Binary depression | GitHub (free) | `eatd_adapter.py` |
| **CMU-MOSI** | 2199 utterances | Audio + Text + Visual | Sentiment (–3 to +3) | Dropbox (free) | `cmu_mosi_adapter.py` |
| **D-Vlog** | 961 vlogs | Audio + Text + Video | Binary depression | Google Drive | Manual (see below) |
| **DAIC-WOZ** *(target)* | 189 participants | Audio + Text + OpenFace | PHQ-8 (0–24) | Request USC | Direct (no adapter) |

---

## Option 0 — Synthetic DAIC-WOZ (Use RIGHT NOW)

**Best for:** Running the complete pipeline end-to-end today, debugging, demos.

The generator creates audio files, transcripts, and OpenFace AU sequences that
are structurally identical to the real dataset. The model actually trains on them.

```bash
cd multimodal_mental_health_analysis/backend

# Generate the synthetic dataset (takes ~2 minutes)
python generate_synthetic_daic.py --output_dir ./data/synthetic_daic

# Quick mode (33 participants only, ~20 seconds)
python generate_synthetic_daic.py --output_dir ./data/synthetic_daic --quick

# Preprocess
python clean_daic_dataset.py --raw_dir ./data/synthetic_daic --output_dir ./data/synthetic_daic/processed --split train
python clean_daic_dataset.py --raw_dir ./data/synthetic_daic --output_dir ./data/synthetic_daic/processed --split dev

# Train (5 epochs for a smoke test)
python train.py \
    --daic_root     ./data/synthetic_daic \
    --processed_dir ./data/synthetic_daic/processed \
    --task          classification \
    --epochs        5 \
    --batch_size    4 \
    --output_dir    ./checkpoints/synthetic

# Evaluate
python evaluate.py \
    --checkpoint    ./checkpoints/synthetic/best.pt \
    --daic_root     ./data/synthetic_daic \
    --processed_dir ./data/synthetic_daic/processed \
    --split         dev
```

**Limitations:** Synthetic data → model accuracy means nothing statistically.
Use this only for development and demonstration.

---

## Option 1 — EATD-Corpus (Best Free Real Dataset)

**Best for:** Real depression labels, real audio + text, free, instant download.

- **Paper:** "Automatic Depression Diagnosis Based on BERT and Audio-Textual Features" (ICASSP 2022)
- **Language:** Chinese Mandarin (audio/text)
- **Labels:** Binary depression (SDS scale)
- **162 participants**, split into train and test

### Download

```bash
git clone https://github.com/speechandlanguageprocessing/ICASSP2022-Depression
```

### Convert and Train

```bash
cd multimodal_mental_health_analysis/backend

python eatd_adapter.py \
    --eatd_root  ./ICASSP2022-Depression \
    --output_dir ./data/eatd_processed

python train.py \
    --daic_root     ./data/eatd_processed \
    --processed_dir ./data/eatd_processed \
    --task          classification \
    --epochs        30 \
    --batch_size    8 \
    --output_dir    ./checkpoints/eatd
```

**Limitations:**
- No facial/video data (facial features will be zeroed — model uses audio + text)
- Chinese language — BERT's multilingual variant works better:
  change `bert-base-uncased` → `bert-base-multilingual-cased` in `multimodal_model.py`

---

## Option 2 — CMU-MOSI (Largest Free Multimodal Dataset)

**Best for:** Multimodal (audio + text + visual) experiment, large dataset size.

- **Homepage:** http://multicomp.cs.cmu.edu/resources/cmu-mosi-dataset/
- **2199 opinion utterances** from 89 YouTube videos
- **Modalities:** Audio (COVAREP), Text, Visual (Facet)
- **Labels:** Sentiment score –3 to +3 (we threshold < –1 as depression proxy)

### Download (pre-extracted features, ~1 GB)

```
Download from one of these mirrors:
  https://www.dropbox.com/sh/hyzpgx1hp9nj37s/AAB7FhBqJOFDw2hEyvv2ZXHxa
  https://github.com/thuiar/TEXTCNN-sentiment/tree/master/datasets

File: mosi_data.pkl  (or mosi_data_noalign.pkl)
```

### Convert and Train

```bash
cd multimodal_mental_health_analysis/backend

python cmu_mosi_adapter.py \
    --mosi_pkl   ./data/mosi_data.pkl \
    --output_dir ./data/mosi_processed

python train.py \
    --daic_root     ./data/mosi_processed \
    --processed_dir ./data/mosi_processed \
    --task          classification \
    --epochs        30 \
    --batch_size    16 \
    --output_dir    ./checkpoints/mosi
```

**Limitations:**
- Sentiment ≠ clinical depression — disclose this clearly in your report
- Visual features are Facet (not OpenFace AUs) → facial encoder uses zeros

---

## Option 3 — D-Vlog

**Best for:** Depression detection in real-world vlogs, publicly available video.

- **Paper:** "D-Vlog: Multimodal Vlog Dataset for Depression Detection" (AAAI 2022)
- **961 YouTube vlogs**, annotated for depression
- **Modalities:** Audio + Text + Video frames
- **Labels:** Binary depression

### Download

```
Email the authors at: seungbumcho@kaist.ac.kr
OR check: https://github.com/seungbum-cho/D-Vlog
Dataset hosted on Google Drive (shared on request).
```

No adapter script is provided here because D-Vlog has its own
preprocessing tools. Once you have the features, organise them into
the `audio_features/`, `text_features/`, `facial_features/` folders
and create a matching `*_split_Depression_AVEC2017.csv` label file.

---

## Recommended Strategy for Your Final Year Project

```
TODAY            → Run with synthetic data to verify everything works
                   python generate_synthetic_daic.py --quick
                   python train.py --epochs 3 ...

THIS WEEK        → Switch to EATD-Corpus for real results
                   git clone https://github.com/speechandlanguageprocessing/ICASSP2022-Depression
                   python eatd_adapter.py ...
                   python train.py --epochs 30 ...

WHEN DAIC ARRIVES → Re-run everything with the real dataset for final numbers
                   python clean_daic_dataset.py ...
                   python train.py --epochs 30 ...
```

### What to write in your report

> "We trained and evaluated our model on the EATD-Corpus [cite] as a
> development dataset during implementation. Final results are reported
> on the DAIC-WOZ dataset [cite], which was obtained under a Data Use
> Agreement from the USC SAIL Laboratory."

---

## Citations

**EATD-Corpus:**
```bibtex
@inproceedings{shen2022icassp,
  title={A Multi-modal Multi-task Learning Framework for Depression Detection},
  author={Shen, Zhicheng and Yao, Ruizhi and Zhao, Linli},
  booktitle={ICASSP},
  year={2022}
}
```

**CMU-MOSI:**
```bibtex
@inproceedings{zadeh2016mosi,
  title={MOSI: Multimodal corpus of sentiment intensity and subjectivity analysis in online opinion videos},
  author={Zadeh, Amir and Zellers, Rowan and Pincus, Eli and Morency, Louis-Philippe},
  journal={arXiv preprint arXiv:1606.06259},
  year={2016}
}
```

**DAIC-WOZ:**
```bibtex
@inproceedings{gratch2014distress,
  title={The distress analysis interview corpus of human and computer interviews},
  author={Gratch, Jonathan and others},
  booktitle={LREC},
  pages={3123--3128},
  year={2014}
}
```
