"""
DAIC-WOZ Evaluation Script
============================
Loads a saved checkpoint and evaluates it on the dev (or test) split,
printing the full set of AVEC/INTERSPEECH standard metrics.

Usage
-----
  python evaluate.py --checkpoint ./checkpoints/best.pt \\
                     --daic_root  /data/daic-woz \\
                     --processed_dir /data/daic-woz/processed \\
                     --split dev

Arguments
---------
  --checkpoint    : path to saved .pt checkpoint (from train.py)
  --daic_root     : folder with *_split_Depression_AVEC2017.csv files
  --processed_dir : folder with audio_features/, text_features/, facial_features/
  --raw_audio_dir : (optional) raw DAIC-WOZ root for on-the-fly mel extraction
  --split         : which split to evaluate: 'dev' (default) or 'test'
  --batch_size    : batch size (default 8)
  --output_json   : (optional) path to save metrics as JSON
  --no_cuda       : force CPU
  --show_weights  : print per-sample modality attention weights
"""

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score, precision_score, recall_score, accuracy_score,
    roc_auc_score,
)
from torch.utils.data import DataLoader

from dataset import DAICWOZDataset
from multimodal_model import build_model


# ──────────────────────────────────────────────────────────────────────────────
# Metric helpers
# ──────────────────────────────────────────────────────────────────────────────

def rmse(p, t):
    return float(np.sqrt(np.mean((p - t) ** 2)))

def mae(p, t):
    return float(np.mean(np.abs(p - t)))

def pcc(p, t):
    """Pearson correlation coefficient."""
    if np.std(p) == 0 or np.std(t) == 0:
        return 0.0
    return float(np.corrcoef(p, t)[0, 1])


# ──────────────────────────────────────────────────────────────────────────────
# Main evaluation loop
# ──────────────────────────────────────────────────────────────────────────────

@torch.no_grad()
def run_evaluation(model, loader, device, task, show_weights=False):
    model.eval()
    all_preds, all_labels, all_probs = [], [], []
    modality_weights = {'audio': [], 'text': [], 'facial': []}

    for batch in loader:
        batch_dev = {k: (v.to(device) if torch.is_tensor(v) else v)
                     for k, v in batch.items()}

        out = model(
            audio     = batch_dev['audio'],
            text_ids  = batch_dev['text_ids'],
            text_mask = batch_dev['text_mask'],
            facial    = batch_dev['facial'],
        )

        if task == 'classification':
            probs = torch.softmax(out, dim=1)[:, 1].cpu().numpy()
            preds = out.argmax(dim=1).cpu().numpy()
            all_probs.extend(probs.tolist())
        else:
            preds = out.cpu().numpy()

        all_preds.extend(preds.tolist())
        all_labels.extend(batch['label'].numpy().tolist())

        if show_weights:
            w = model.get_modality_weights(
                batch_dev['audio'],
                batch_dev['text_ids'],
                batch_dev['text_mask'],
                batch_dev['facial'],
            )
            for key in modality_weights:
                modality_weights[key].extend(w[key].tolist())

    all_preds  = np.array(all_preds)
    all_labels = np.array(all_labels)

    return all_preds, all_labels, all_probs, modality_weights


# ──────────────────────────────────────────────────────────────────────────────
# Compute and print metrics
# ──────────────────────────────────────────────────────────────────────────────

def compute_metrics(preds, labels, probs, task):
    metrics = {}
    if task == 'classification':
        metrics['accuracy']  = float(accuracy_score(labels, preds))
        metrics['f1']        = float(f1_score(labels, preds, zero_division=0))
        metrics['precision'] = float(precision_score(labels, preds, zero_division=0))
        metrics['recall']    = float(recall_score(labels, preds, zero_division=0))
        try:
            metrics['auc'] = float(roc_auc_score(labels, probs))
        except ValueError:
            metrics['auc'] = 0.0
    else:
        metrics['rmse'] = rmse(preds, labels)
        metrics['mae']  = mae(preds, labels)
        metrics['pcc']  = pcc(preds, labels)
        # AVEC standard: also binary F1 using threshold 10
        bin_preds  = (preds >= 10.0).astype(int)
        bin_labels = (labels >= 10.0).astype(int)
        metrics['f1_binary']  = float(f1_score(bin_labels, bin_preds, zero_division=0))
        metrics['acc_binary'] = float(accuracy_score(bin_labels, bin_preds))
    return metrics


def print_metrics(metrics, task, preds, labels, probs):
    sep = "=" * 60
    print(f"\n{sep}")
    print("  EVALUATION RESULTS")
    print(sep)
    for k, v in metrics.items():
        print(f"  {k:<20}: {v:.4f}")

    if task == 'classification':
        print(f"\n  Confusion Matrix:")
        cm = confusion_matrix(labels, preds)
        print(f"           Predicted")
        print(f"           Non-dep  Dep")
        print(f"  Non-dep  {cm[0,0]:6d}  {cm[0,1]:4d}")
        print(f"  Dep      {cm[1,0]:6d}  {cm[1,1]:4d}")
        print(f"\n  Classification Report:")
        print(classification_report(
            labels, preds,
            target_names=['Non-Depressed', 'Depressed']
        ))
    else:
        print(f"\n  Score distribution (predictions):")
        print(f"    min={preds.min():.2f}  max={preds.max():.2f}  "
              f"mean={preds.mean():.2f}  std={preds.std():.2f}")
        print(f"  Score distribution (ground truth):")
        print(f"    min={labels.min():.2f}  max={labels.max():.2f}  "
              f"mean={labels.mean():.2f}  std={labels.std():.2f}")
    print(sep)


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description='Evaluate DAIC-WOZ multimodal model')
    p.add_argument('--checkpoint',    required=True)
    p.add_argument('--daic_root',     required=True)
    p.add_argument('--processed_dir', required=True)
    p.add_argument('--raw_audio_dir', default=None)
    p.add_argument('--split',         default='dev', choices=['dev', 'test'])
    p.add_argument('--batch_size',    type=int, default=8)
    p.add_argument('--output_json',   default=None,
                   help='If set, write metrics to this JSON file')
    p.add_argument('--no_cuda',       action='store_true')
    p.add_argument('--show_weights',  action='store_true',
                   help='Print average modality attention weights')
    return p.parse_args()


def main():
    args = parse_args()

    use_cuda = torch.cuda.is_available() and not args.no_cuda
    device   = torch.device('cuda' if use_cuda else 'cpu')
    print(f"[evaluate] Device : {device}")

    # ── Load checkpoint ──────────────────────────────────────────────────
    ckpt = torch.load(args.checkpoint, map_location=device)
    train_args = ckpt.get('args', {})
    task       = train_args.get('task', 'classification')
    embed_dim  = train_args.get('embed_dim', 256)
    dropout    = train_args.get('dropout', 0.3)

    print(f"[evaluate] Task      : {task}")
    print(f"[evaluate] Split     : {args.split}")
    print(f"[evaluate] Checkpoint: {args.checkpoint}")

    # ── Dataset ──────────────────────────────────────────────────────────
    daic_root = Path(args.daic_root)
    label_csv = daic_root / f'{args.split}_split_Depression_AVEC2017.csv'
    if not label_csv.exists():
        # Fallback: some downloads use 'validation' for dev
        label_csv = daic_root / f'{'dev' if args.split == 'dev' else args.split}_split_Depression_AVEC2017.csv'

    dataset = DAICWOZDataset(
        labels_csv    = str(label_csv),
        processed_dir = args.processed_dir,
        raw_audio_dir = args.raw_audio_dir,
        task          = task,
        use_bert      = True,
        augment       = False,
    )
    loader = DataLoader(dataset, batch_size=args.batch_size,
                        shuffle=False, num_workers=0, pin_memory=True)

    # ── Model ────────────────────────────────────────────────────────────
    model = build_model(task=task, embed_dim=embed_dim, dropout=dropout).to(device)
    model.load_state_dict(ckpt['model_state'])
    print(f"[evaluate] Model loaded from epoch {ckpt.get('epoch', '?')}")

    # ── Run ──────────────────────────────────────────────────────────────
    preds, labels, probs, mod_weights = run_evaluation(
        model, loader, device, task, show_weights=args.show_weights
    )
    metrics = compute_metrics(preds, labels, probs, task)
    print_metrics(metrics, task, preds, labels, probs)

    # ── Modality attention weights ────────────────────────────────────────
    if args.show_weights and any(mod_weights.values()):
        print("\n  Average modality attention weights:")
        for k, v in mod_weights.items():
            print(f"    {k:<8}: {np.mean(v):.4f}")

    # ── Save JSON ────────────────────────────────────────────────────────
    if args.output_json:
        with open(args.output_json, 'w') as f:
            json.dump(metrics, f, indent=2)
        print(f"\n[evaluate] Metrics saved to: {args.output_json}")


if __name__ == '__main__':
    main()
