"""Quick result inspector — reads checkpoints without reloading the model."""
import json, os, torch
from pathlib import Path

base = Path(__file__).parent / 'checkpoints' / 'eatd'

files = list(base.glob('*.pt')) + list(base.glob('*.json'))
print("Files in eatd checkpoint dir:")
for f in files:
    print("  ", f.name, f.stat().st_size, "bytes")

# Read last.pt metadata only (no model weights)
last = base / 'last.pt'
if last.exists():
    ckpt = torch.load(str(last), map_location='cpu', weights_only=False)
    print("\n--- last.pt metadata ---")
    print("  epoch      :", ckpt.get('epoch'))
    print("  best_metric:", ckpt.get('best_metric'))
    h = ckpt.get('history', {})
    if isinstance(h, dict):
        train_h = h.get('train', [])
        dev_h   = h.get('dev', [])
        print("  history epochs (train):", len(train_h))
        print("  history epochs (dev)  :", len(dev_h))
        print()
        print("  Epoch  TrainLoss  TrainAcc  TrainF1  DevAcc  DevF1")
        for tr, dv in zip(train_h, dev_h):
            print("  {:5}  {:9.4f}  {:8.3f}  {:7.3f}  {:6.3f}  {:5.3f}".format(
                tr['epoch']+1, tr['loss'], tr['accuracy'], tr.get('f1', 0),
                dv['accuracy'], dv.get('f1', 0)
            ))
