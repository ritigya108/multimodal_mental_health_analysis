"""
CPU-Fast Multimodal Training Script
=====================================
Same architecture as multimodal_model.py but replaces BERT with
a lightweight TF-IDF + MLP text encoder so 30 epochs run in ~5 minutes
on any CPU — no GPU, no BERT download needed.

Audio  → CNN (4 blocks)           → 256-d
Text   → TF-IDF(500) + MLP        → 256-d   (replaces BERT for CPU speed)
Facial → BiLSTM (2 layers)        → 256-d
Fusion → Cross-modal Attention    → MLP head → PHQ8_Binary

Usage
-----
  python train_cpu_fast.py ^
      --daic_root     .\\data\\eatd_processed ^
      --processed_dir .\\data\\eatd_processed ^
      --epochs        30 ^
      --batch_size    16 ^
      --output_dir    .\\checkpoints\\eatd_fast
"""

import argparse
import json
import os
import random
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import f1_score, accuracy_score, precision_score, recall_score, classification_report
from sklearn.preprocessing import normalize

# ── Constants (same as dataset.py) ────────────────────────────────────────────
N_MELS        = 128
MAX_AU_FRAMES = 300
N_AU          = 17
TFIDF_DIM     = 500
EMBED_DIM     = 256
DROPOUT       = 0.3

AU_COLS = [
    'AU01_r','AU02_r','AU04_r','AU05_r','AU06_r','AU07_r',
    'AU09_r','AU10_r','AU12_r','AU14_r','AU15_r','AU17_r',
    'AU20_r','AU23_r','AU25_r','AU26_r','AU45_r',
]


# ── Model ─────────────────────────────────────────────────────────────────────

class AudioEncoderFast(nn.Module):
    def __init__(self, embed_dim=EMBED_DIM, dropout=DROPOUT):
        super().__init__()
        self.cnn = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(True), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(True), nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(True), nn.MaxPool2d(2),
            nn.Conv2d(128, 256, 3, padding=1), nn.BatchNorm2d(256), nn.ReLU(True),
            nn.AdaptiveAvgPool2d((4, 4)),
        )
        self.proj = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256 * 4 * 4, 512), nn.ReLU(True), nn.Dropout(dropout),
            nn.Linear(512, embed_dim),
        )
    def forward(self, x): return self.proj(self.cnn(x))


class TextEncoderFast(nn.Module):
    """Lightweight TF-IDF + MLP — no BERT, runs instantly on CPU."""
    def __init__(self, tfidf_dim=TFIDF_DIM, embed_dim=EMBED_DIM, dropout=DROPOUT):
        super().__init__()
        self.proj = nn.Sequential(
            nn.Linear(tfidf_dim, 512), nn.ReLU(True), nn.Dropout(dropout),
            nn.Linear(512, embed_dim),
        )
    def forward(self, x): return self.proj(x)   # x: (B, tfidf_dim)


class FacialEncoderFast(nn.Module):
    def __init__(self, n_au=N_AU, hidden=128, embed_dim=EMBED_DIM, dropout=DROPOUT):
        super().__init__()
        self.bilstm = nn.LSTM(n_au, hidden, num_layers=2, batch_first=True,
                              bidirectional=True, dropout=dropout)
        self.proj = nn.Sequential(nn.Linear(hidden * 2, embed_dim), nn.ReLU(True), nn.Dropout(dropout))
    def forward(self, x):
        _, (h, _) = self.bilstm(x)
        return self.proj(torch.cat([h[-2], h[-1]], dim=-1))


class FusionFast(nn.Module):
    def __init__(self, embed_dim=EMBED_DIM, dropout=DROPOUT):
        super().__init__()
        self.w_a = nn.Linear(embed_dim, 1)
        self.w_t = nn.Linear(embed_dim, 1)
        self.w_f = nn.Linear(embed_dim, 1)
        self.norm = nn.LayerNorm(embed_dim)
        self.mlp  = nn.Sequential(nn.Linear(embed_dim, embed_dim), nn.ReLU(True), nn.Dropout(dropout))
    def forward(self, a, t, f):
        ws = F.softmax(torch.stack([self.w_a(a), self.w_t(t), self.w_f(f)], dim=1), dim=1)
        fused = (ws * torch.stack([a, t, f], dim=1)).sum(dim=1)
        return self.mlp(self.norm(fused))


class FastMultimodalModel(nn.Module):
    def __init__(self, tfidf_dim=TFIDF_DIM, embed_dim=EMBED_DIM, dropout=DROPOUT):
        super().__init__()
        self.audio_enc  = AudioEncoderFast(embed_dim, dropout)
        self.text_enc   = TextEncoderFast(tfidf_dim, embed_dim, dropout)
        self.facial_enc = FacialEncoderFast(N_AU, 128, embed_dim, dropout)
        self.fusion     = FusionFast(embed_dim, dropout)
        self.head       = nn.Sequential(
            nn.Linear(embed_dim, 128), nn.ReLU(True), nn.Dropout(dropout), nn.Linear(128, 2)
        )
    def forward(self, audio, text_vec, facial):
        a = self.audio_enc(audio)
        t = self.text_enc(text_vec)
        f = self.facial_enc(facial)
        return self.head(self.fusion(a, t, f))


# ── Dataset ───────────────────────────────────────────────────────────────────

def _load_audio_npy(path: Path) -> np.ndarray:
    data = np.load(str(path), allow_pickle=True)
    if isinstance(data, np.ndarray) and data.dtype == object:
        data = data.item()
    if isinstance(data, dict):
        arrays = [np.atleast_1d(np.asarray(v, dtype=np.float32)).flatten() for v in data.values()]
        vals = np.concatenate(arrays)
        mel = np.tile(vals[:N_MELS], (N_MELS, 1)).astype(np.float32)
        mel = (mel - mel.min()) / (mel.max() - mel.min() + 1e-8)
    else:
        mel = data.astype(np.float32)
        if mel.ndim == 1:
            mel = np.expand_dims(mel, 0).repeat(N_MELS, axis=0)
    T = 128
    mel = mel[:, :T] if mel.shape[1] >= T else np.pad(mel, ((0, 0), (0, T - mel.shape[1])))
    return mel  # (N_MELS, 128)


def _load_text_raw(path: Path) -> str:
    try:
        df = pd.read_csv(str(path))
        col = 'text_cleaned' if 'text_cleaned' in df.columns else 'value'
        return ' '.join(df[col].dropna().astype(str).tolist()).strip() or '[empty]'
    except Exception:
        return '[empty]'


def _load_facial(path: Path) -> np.ndarray:
    try:
        df = pd.read_csv(str(path))
        df.columns = df.columns.str.strip()
        avail = [c for c in AU_COLS if c in df.columns]
        if not avail:
            return np.zeros((MAX_AU_FRAMES, N_AU), dtype=np.float32)
        arr = df[avail].values.astype(np.float32)
        T = arr.shape[0]
        if T >= MAX_AU_FRAMES:
            arr = arr[:MAX_AU_FRAMES]
        else:
            arr = np.concatenate([arr, np.zeros((MAX_AU_FRAMES - T, arr.shape[1]), dtype=np.float32)])
        if arr.shape[1] < N_AU:
            arr = np.concatenate([arr, np.zeros((MAX_AU_FRAMES, N_AU - arr.shape[1]), dtype=np.float32)], axis=1)
        return arr
    except Exception:
        return np.zeros((MAX_AU_FRAMES, N_AU), dtype=np.float32)


class EATDDataset(Dataset):
    def __init__(self, labels_csv: str, processed_dir: str, tfidf: TfidfVectorizer, augment=False):
        self.pdir   = Path(processed_dir)
        self.augment = augment
        self.tfidf  = tfidf
        df = pd.read_csv(labels_csv)
        df.columns = df.columns.str.strip()
        # keep only participants that have at least audio or text
        valid = []
        for _, row in df.iterrows():
            pid = str(row['Participant_ID']).strip()
            if (self.pdir/'audio_features'/f'{pid}.npy').exists() or \
               (self.pdir/'text_features'/f'{pid}.csv').exists():
                valid.append(pid)
        self.pids   = valid
        self.labels = {str(r['Participant_ID']).strip(): int(r['PHQ8_Binary'])
                       for _, r in df.iterrows()}
        print(f"  Loaded {len(self.pids)} participants from {Path(labels_csv).name}")

    def __len__(self): return len(self.pids)

    def __getitem__(self, idx):
        pid = self.pids[idx]

        # Audio
        apath = self.pdir / 'audio_features' / f'{pid}.npy'
        mel   = _load_audio_npy(apath) if apath.exists() else np.zeros((N_MELS, 128), dtype=np.float32)
        if self.augment:
            f0 = random.randint(0, max(1, N_MELS - 10))
            mel[f0:min(f0 + random.randint(1, 10), N_MELS), :] = 0.0
            t0 = random.randint(0, max(1, 128 - 15))
            mel[:, t0:min(t0 + random.randint(1, 15), 128)] = 0.0
        audio_t = torch.tensor(mel, dtype=torch.float32).unsqueeze(0)  # (1, N_MELS, 128)

        # Text — TF-IDF vector (pre-computed by caller; here we re-fetch the text)
        tpath = self.pdir / 'text_features' / f'{pid}.csv'
        raw_text = _load_text_raw(tpath) if tpath.exists() else '[empty]'
        text_vec = self.tfidf.transform([raw_text]).toarray().astype(np.float32)[0]
        text_t   = torch.tensor(text_vec, dtype=torch.float32)

        # Facial
        fpath   = self.pdir / 'facial_features' / f'{pid}.csv'
        facial  = _load_facial(fpath) if fpath.exists() else np.zeros((MAX_AU_FRAMES, N_AU), dtype=np.float32)
        facial_t = torch.tensor(facial, dtype=torch.float32)

        label = torch.tensor(self.labels[pid], dtype=torch.long)
        return audio_t, text_t, facial_t, label


# ── Training helpers ──────────────────────────────────────────────────────────

def set_seed(seed):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)


def train_epoch(model, loader, opt, criterion, device):
    model.train()
    total_loss, preds_all, labels_all = 0.0, [], []
    for audio, text, facial, label in loader:
        audio, text, facial, label = audio.to(device), text.to(device), facial.to(device), label.to(device)
        opt.zero_grad()
        out  = model(audio, text, facial)
        loss = criterion(out, label)
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        total_loss += loss.item()
        preds_all.extend(out.argmax(1).cpu().tolist())
        labels_all.extend(label.cpu().tolist())
    p, l = np.array(preds_all), np.array(labels_all)
    return total_loss / max(len(loader), 1), {
        'accuracy':  float(accuracy_score(l, p)),
        'f1':        float(f1_score(l, p, zero_division=0)),
        'precision': float(precision_score(l, p, zero_division=0)),
        'recall':    float(recall_score(l, p, zero_division=0)),
    }


@torch.no_grad()
def eval_epoch(model, loader, criterion, device):
    model.eval()
    total_loss, preds_all, labels_all = 0.0, [], []
    for audio, text, facial, label in loader:
        audio, text, facial, label = audio.to(device), text.to(device), facial.to(device), label.to(device)
        out  = model(audio, text, facial)
        loss = criterion(out, label)
        total_loss += loss.item()
        preds_all.extend(out.argmax(1).cpu().tolist())
        labels_all.extend(label.cpu().tolist())
    p, l = np.array(preds_all), np.array(labels_all)
    return total_loss / max(len(loader), 1), {
        'accuracy':  float(accuracy_score(l, p)),
        'f1':        float(f1_score(l, p, zero_division=0)),
        'precision': float(precision_score(l, p, zero_division=0)),
        'recall':    float(recall_score(l, p, zero_division=0)),
    }, p, l


# ── Main ──────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--daic_root',     required=True)
    p.add_argument('--processed_dir', required=True)
    p.add_argument('--epochs',        type=int,   default=30)
    p.add_argument('--batch_size',    type=int,   default=16)
    p.add_argument('--lr',            type=float, default=3e-4)
    p.add_argument('--output_dir',    default='./checkpoints/eatd_fast')
    p.add_argument('--seed',          type=int,   default=42)
    p.add_argument('--tfidf_dim',     type=int,   default=500)
    return p.parse_args()


def main():
    args = parse_args()
    set_seed(args.seed)
    device = torch.device('cpu')
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    root = Path(args.daic_root)
    proc = Path(args.processed_dir)

    # ── Build TF-IDF on ALL text (train + dev) ────────────────────────────
    print("\n[fast-train] Building TF-IDF vocabulary ...")
    all_texts = []
    for csv_f in (proc / 'text_features').glob('*.csv'):
        all_texts.append(_load_text_raw(csv_f))
    if not all_texts:
        all_texts = ['[empty]']
    tfidf = TfidfVectorizer(max_features=args.tfidf_dim, sublinear_tf=True,
                            ngram_range=(1, 2), min_df=1)
    tfidf.fit(all_texts)
    print(f"[fast-train] TF-IDF vocab size: {len(tfidf.vocabulary_)}")

    # ── Datasets ──────────────────────────────────────────────────────────
    train_csv = root / 'train_split_Depression_AVEC2017.csv'
    dev_csv   = root / 'dev_split_Depression_AVEC2017.csv'
    train_ds  = EATDDataset(str(train_csv), str(proc), tfidf, augment=True)
    dev_ds    = EATDDataset(str(dev_csv),   str(proc), tfidf, augment=False)

    # ── Class weights (handle imbalance) ─────────────────────────────────
    df_tr = pd.read_csv(str(train_csv))
    n0 = int((df_tr['PHQ8_Binary'] == 0).sum())
    n1 = int((df_tr['PHQ8_Binary'] == 1).sum())
    total = n0 + n1
    w0 = round(total / (2.0 * max(n0, 1)), 3)
    w1 = round(total / (2.0 * max(n1, 1)), 3)
    print(f"[fast-train] Class weights: non-depressed={w0:.2f}  depressed={w1:.2f}  (n0={n0}, n1={n1})")
    criterion = nn.CrossEntropyLoss(weight=torch.tensor([w0, w1], dtype=torch.float32))

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True,  num_workers=0, drop_last=True)
    dev_loader   = DataLoader(dev_ds,   batch_size=args.batch_size, shuffle=False, num_workers=0)

    # ── Model ─────────────────────────────────────────────────────────────
    model = FastMultimodalModel(tfidf_dim=args.tfidf_dim).to(device)
    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"[fast-train] Trainable parameters: {total_params:,}")

    opt       = AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = CosineAnnealingLR(opt, T_max=args.epochs, eta_min=1e-6)

    best_f1  = 0.0
    history  = {'train': [], 'dev': []}

    print(f"\n[fast-train] Training for {args.epochs} epochs  |  batch={args.batch_size}  |  device=cpu")
    print("=" * 80)

    for epoch in range(args.epochs):
        t0 = time.time()
        tr_loss, tr_m = train_epoch(model, train_loader, opt, criterion, device)
        dv_loss, dv_m, dv_preds, dv_labels = eval_epoch(model, dev_loader, criterion, device)
        scheduler.step()

        history['train'].append({'epoch': epoch, 'loss': tr_loss, **tr_m})
        history['dev'].append(  {'epoch': epoch, 'loss': dv_loss, **dv_m})

        print(
            f"Epoch {epoch+1:03d}/{args.epochs} | "
            f"Train loss={tr_loss:.4f} acc={tr_m['accuracy']:.3f} f1={tr_m['f1']:.3f} | "
            f"Dev   loss={dv_loss:.4f} acc={dv_m['accuracy']:.3f} f1={dv_m['f1']:.3f} | "
            f"{time.time()-t0:.1f}s"
        )

        # Save last checkpoint every epoch
        ckpt = {
            'epoch': epoch, 'model_state': model.state_dict(),
            'optimizer_state': opt.state_dict(),
            'best_f1': best_f1, 'history': history,
            'tfidf_vocab': tfidf.vocabulary_,
            'tfidf_idf':   tfidf.idf_.tolist(),
            'args': vars(args),
        }
        torch.save(ckpt, out_dir / 'last.pt')

        if dv_m['f1'] > best_f1:
            best_f1 = dv_m['f1']
            torch.save(ckpt, out_dir / 'best.pt')
            print(f"  *** NEW BEST F1={best_f1:.4f} — saved best.pt ***")

    # ── Final evaluation ─────────────────────────────────────────────────
    print("\n" + "=" * 80)
    best_pt = out_dir / 'best.pt'
    if not best_pt.exists():
        best_pt = out_dir / 'last.pt'
    best_ckpt = torch.load(str(best_pt), map_location='cpu')
    model.load_state_dict(best_ckpt['model_state'])
    _, final_m, final_preds, final_labels = eval_epoch(model, dev_loader, criterion, device)

    print("\n[fast-train] Final Dev Metrics:")
    for k, v in final_m.items():
        print(f"  {k}: {v:.4f}")
    print("\nClassification Report:")
    print(classification_report(final_labels, final_preds,
                                 target_names=['Non-Depressed', 'Depressed']))

    with open(out_dir / 'final_metrics.json', 'w') as f:
        json.dump(final_m, f, indent=2)
    with open(out_dir / 'history.json', 'w') as f:
        json.dump(history, f, indent=2)

    print(f"\n[fast-train] Done. Best F1={best_f1:.4f}  Checkpoints → {out_dir}")


if __name__ == '__main__':
    main()
