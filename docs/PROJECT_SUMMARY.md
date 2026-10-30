# Project Summary — Multimodal Depression Screening using EATD-Corpus

## Problem

Depression is underdiagnosed globally, partly because conventional screening tools
(PHQ-8, SDS) rely solely on self-report and require clinical administration. Automated,
non-intrusive screening that combines acoustic and linguistic cues could help bridge
this gap, particularly in low-resource settings.

## Objective

Build a bimodal (audio + text) depression detection system trained on the EATD-Corpus
that classifies participants as depressed / non-depressed and exposes a REST API,
a React dashboard, and a Streamlit demo interface.

---

## Architecture

```
Audio  → mel-spectrogram → CNN encoder        ┐
                                               ├→ Cross-modal Attention Fusion → MLP head → label
Text   → BERT tokenizer  → BiLSTM / projection ┘
```

Three branch experiments were run independently before fusion:

| Branch | Encoder | Features |
|--------|---------|----------|
| CNN    | 2D CNN on mel-spectrograms | 128-band mel, 60 s audio |
| LSTM   | Unidirectional LSTM on TF-IDF | 512-dim TF-IDF vectors |
| BiLSTM | Bidirectional LSTM on BERT embeddings | last-2-layer BERT fine-tune |
| Fusion | Late cross-modal attention | audio (256-d) + text (256-d) → 512-d |

---

## Dataset

**EATD-Corpus** (Shen et al., ICASSP 2022)

- ~162 participants; Mandarin audio + text transcripts
- Three emotional questions per participant (positive, neutral, negative)
- Labels: SDS (Self-Rating Depression Scale) scores → binary threshold ≥ 53
- Class imbalance: ~78% non-depressed / ~22% depressed

---

## Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI 0.104, Python 3.9 |
| Frontend | React 18, MUI v5 |
| Demo app | Streamlit 1.x |
| ML | PyTorch 2.x, HuggingFace Transformers 4.x |
| Audio | librosa 0.10 |
| Containerisation | Docker Compose |

---

## Results

See [`ml/results/metrics.json`](../ml/results/metrics.json).  
All values are placeholders until real training is completed.

---

## Key design decisions

1. **Bimodal only** — EATD-Corpus has no video; a three-modal architecture would require
   a different dataset. Video modality is documented as future work.
2. **Heuristic fallback** — the API works without a checkpoint using rule-based linguistic
   feature extraction, enabling demo use before training is complete.
3. **Crisis safety** — every page surface shows a configurable crisis helpline; high-risk
   assessments trigger a prominent banner.
4. **No clinical claims** — all outputs carry a disclaimer that this is a screening tool,
   not a diagnosis.
