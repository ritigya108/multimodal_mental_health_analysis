"""
Multimodal Depression Screening — Master Pipeline Runner
=========================================================
Run this ONE script from ANYWHERE to execute the full pipeline.

Usage
-----
  # With EATD-Corpus (obtain from https://github.com/speechandlanguageprocessing/ICASSP2022-Depression):
  python run_pipeline.py --mode eatd --eatd_root C:/data/ICASSP2022-Depression

  # With synthetic data (no dataset needed, works right now):
  python run_pipeline.py --mode synthetic

  # Evaluate a saved checkpoint:
  python run_pipeline.py --mode evaluate --checkpoint ./backend/checkpoints/best.pt

Arguments
---------
  --mode         : synthetic | eatd | evaluate  (default: synthetic)
  --eatd_root    : path to EATD-Corpus root folder (required for --mode eatd)
  --checkpoint   : path to .pt file (required for --mode evaluate)
  --task         : classification | regression  (default: classification)
  --epochs       : number of training epochs   (default: 30)
  --batch_size   : batch size                  (default: 8)
  --lr           : learning rate               (default: 2e-4)
  --quick        : use smaller synthetic dataset for quick testing
  --eval_only    : skip training, only evaluate using --checkpoint
  --output_dir   : where to save checkpoints   (default: ./backend/checkpoints)
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# ── Resolve paths relative to THIS file, not the working directory ──────────
PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND      = PROJECT_ROOT / "backend"


def run(cmd: list, cwd: Path = None):
    """Run a command, streaming output live, exit on failure."""
    cwd = cwd or BACKEND
    print(f"\n[pipeline] Running: {' '.join(str(c) for c in cmd)}")
    print(f"           In:      {cwd}")
    print("-" * 60)
    result = subprocess.run(
        [sys.executable] + [str(c) for c in cmd],
        cwd=str(cwd),
    )
    if result.returncode != 0:
        print(f"\n[pipeline] ERROR: command failed (exit {result.returncode})")
        sys.exit(result.returncode)


def banner(title: str):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


# ─────────────────────────────────────────────────────────────────────────────
# MODE: synthetic
# ─────────────────────────────────────────────────────────────────────────────

def run_synthetic(args):
    banner("MODE: Synthetic DAIC-WOZ")
    data_dir      = BACKEND / "data" / "synthetic_daic"
    processed_dir = data_dir / "processed"
    output_dir    = BACKEND / args.output_dir / "synthetic"

    # Step 1 — Generate synthetic data
    banner("Step 1/4 — Generating synthetic DAIC-WOZ data")
    gen_args = ["generate_synthetic_daic.py",
                "--output_dir", data_dir,
                "--seed", "42"]
    if args.quick:
        gen_args.append("--quick")
    run(gen_args)

    # Step 2 — Preprocess (lenient, no quality gates)
    banner("Step 2/4 — Preprocessing (train split)")
    run(["preprocess_synthetic.py",
         "--raw_dir",    data_dir,
         "--output_dir", processed_dir,
         "--split",      "train"])

    banner("Step 2/4 — Preprocessing (dev split)")
    run(["preprocess_synthetic.py",
         "--raw_dir",    data_dir,
         "--output_dir", processed_dir,
         "--split",      "dev"])

    # Step 3 — Train
    if not args.eval_only:
        banner("Step 3/4 — Training")
        train_args = [
            "train.py",
            "--daic_root",     data_dir,
            "--processed_dir", processed_dir,
            "--task",          args.task,
            "--epochs",        args.epochs,
            "--batch_size",    args.batch_size,
            "--lr",            args.lr,
            "--output_dir",    output_dir,
        ]
        if not _has_gpu():
            train_args.append("--no_cuda")
        run(train_args)

    # Step 4 — Evaluate
    banner("Step 4/4 — Evaluating best checkpoint")
    ckpt = args.checkpoint or str(output_dir / "best.pt")
    eval_args = [
        "evaluate.py",
        "--checkpoint",    ckpt,
        "--daic_root",     data_dir,
        "--processed_dir", processed_dir,
        "--split",         "dev",
        "--show_weights",
    ]
    if not _has_gpu():
        eval_args.append("--no_cuda")
    run(eval_args)

    banner("Pipeline complete!")
    print(f"  Checkpoints : {output_dir}")
    print(f"  Best model  : {output_dir}/best.pt")
    _print_next_steps("synthetic", data_dir, processed_dir)


# ─────────────────────────────────────────────────────────────────────────────
# MODE: daic  (real DAIC-WOZ dataset)
# ─────────────────────────────────────────────────────────────────────────────

def run_daic(args):
    if not args.daic_root:
        print("[pipeline] ERROR: --daic_root is required for --mode daic")
        print("           Example: python run_pipeline.py --mode daic --daic_root C:/data/daic-woz")
        sys.exit(1)

    daic_root     = Path(args.daic_root)
    processed_dir = daic_root / "processed"
    output_dir    = BACKEND / args.output_dir / "daic"

    banner("MODE: Real DAIC-WOZ Dataset")
    print(f"  Dataset root : {daic_root}")

    # Verify label files exist
    for split in ["train", "dev"]:
        csv = daic_root / f"{split}_split_Depression_AVEC2017.csv"
        if not csv.exists():
            print(f"[pipeline] ERROR: Label file not found: {csv}")
            print("           Make sure you downloaded the full DAIC-WOZ dataset.")
            sys.exit(1)

    # Step 1 — Preprocess all splits using the full quality-checked cleaner
    if not args.eval_only:
        for split in ["train", "dev"]:
            banner(f"Step 1/3 — Preprocessing ({split} split)")
            run(["clean_daic_dataset.py",
                 "--raw_dir",    daic_root,
                 "--output_dir", processed_dir,
                 "--split",      split])

        # Step 2 — Train
        banner("Step 2/3 — Training")
        train_args = [
            "train.py",
            "--daic_root",     daic_root,
            "--processed_dir", processed_dir,
            "--task",          args.task,
            "--epochs",        args.epochs,
            "--batch_size",    args.batch_size,
            "--lr",            args.lr,
            "--output_dir",    output_dir,
        ]
        if not _has_gpu():
            train_args.append("--no_cuda")
        run(train_args)

    # Step 3 — Evaluate
    banner("Step 3/3 — Evaluating best checkpoint")
    ckpt = args.checkpoint or str(output_dir / "best.pt")
    eval_args = [
        "evaluate.py",
        "--checkpoint",    ckpt,
        "--daic_root",     daic_root,
        "--processed_dir", processed_dir,
        "--split",         "dev",
        "--show_weights",
    ]
    if not _has_gpu():
        eval_args.append("--no_cuda")
    run(eval_args)

    banner("Pipeline complete!")
    print(f"  Checkpoints : {output_dir}")
    _print_next_steps("daic", daic_root, processed_dir)


# ─────────────────────────────────────────────────────────────────────────────
# MODE: eatd  (free EATD-Corpus)
# ─────────────────────────────────────────────────────────────────────────────

def run_eatd(args):
    if not args.eatd_root:
        print("[pipeline] ERROR: --eatd_root is required for --mode eatd")
        print("           Clone the repo first:")
        print("           git clone https://github.com/speechandlanguageprocessing/ICASSP2022-Depression")
        print("           Then: python run_pipeline.py --mode eatd --eatd_root ./ICASSP2022-Depression")
        sys.exit(1)

    eatd_root     = Path(args.eatd_root)
    processed_dir = BACKEND / "data" / "eatd_processed"
    output_dir    = BACKEND / args.output_dir / "eatd"

    banner("MODE: EATD-Corpus (Free Depression Dataset)")
    print(f"  EATD root    : {eatd_root}")

    if not args.eval_only:
        # Step 1 — Convert EATD to DAIC-WOZ format
        banner("Step 1/3 — Converting EATD-Corpus to pipeline format")
        run(["eatd_adapter.py",
             "--eatd_root",  eatd_root,
             "--output_dir", processed_dir])

        # Step 2 — Train
        banner("Step 2/3 — Training")
        train_args = [
            "train.py",
            "--daic_root",     processed_dir,
            "--processed_dir", processed_dir,
            "--task",          args.task,
            "--epochs",        args.epochs,
            "--batch_size",    args.batch_size,
            "--lr",            args.lr,
            "--output_dir",    output_dir,
        ]
        if not _has_gpu():
            train_args.append("--no_cuda")
        run(train_args)

    # Step 3 — Evaluate
    banner("Step 3/3 — Evaluating best checkpoint")
    ckpt = args.checkpoint or str(output_dir / "best.pt")
    eval_args = [
        "evaluate.py",
        "--checkpoint",    ckpt,
        "--daic_root",     processed_dir,
        "--processed_dir", processed_dir,
        "--split",         "dev",
        "--show_weights",
    ]
    if not _has_gpu():
        eval_args.append("--no_cuda")
    run(eval_args)

    banner("Pipeline complete!")
    print(f"  Checkpoints : {output_dir}")


# ─────────────────────────────────────────────────────────────────────────────
# MODE: evaluate only
# ─────────────────────────────────────────────────────────────────────────────

def run_evaluate(args):
    if not args.checkpoint:
        # Auto-find the most recent best.pt
        ckpts = list((BACKEND / "checkpoints").rglob("best.pt"))
        if not ckpts:
            print("[pipeline] ERROR: No checkpoint found. Train first or pass --checkpoint path/to/best.pt")
            sys.exit(1)
        ckpt = str(sorted(ckpts, key=lambda p: p.stat().st_mtime)[-1])
        print(f"[pipeline] Auto-selected checkpoint: {ckpt}")
    else:
        ckpt = args.checkpoint

    # Try to infer data locations from checkpoint's args JSON
    ckpt_dir  = Path(ckpt).parent
    json_path = ckpt_dir / "final_metrics.json"
    hist_path = ckpt_dir / "history.json"

    import torch, json as _json
    saved = torch.load(ckpt, map_location="cpu")
    saved_args = saved.get("args", {})

    daic_root     = args.daic_root or saved_args.get("daic_root")
    processed_dir = args.processed_dir or saved_args.get("processed_dir")

    if not daic_root or not processed_dir:
        print("[pipeline] ERROR: Cannot infer --daic_root / --processed_dir from checkpoint.")
        print("           Pass them explicitly:")
        print("           python run_pipeline.py --mode evaluate --checkpoint ... --daic_root ... --processed_dir ...")
        sys.exit(1)

    banner("MODE: Evaluate checkpoint")
    eval_args = [
        "evaluate.py",
        "--checkpoint",    ckpt,
        "--daic_root",     daic_root,
        "--processed_dir", processed_dir,
        "--split",         "dev",
        "--show_weights",
    ]
    if not _has_gpu():
        eval_args.append("--no_cuda")
    run(eval_args)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _has_gpu() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


def _print_next_steps(mode: str, data_dir, processed_dir):
    print()
    print("  Next steps:")
    if mode == "synthetic":
        print("  1. Get the real DAIC-WOZ dataset from https://dcapswoz.ict.usc.edu/")
        print("  2. Run:  python run_pipeline.py --mode daic --daic_root <path>")
        print("     No other changes needed — the pipeline handles everything.")
    elif mode == "daic":
        print("  1. Switch to regression task:")
        print("     python run_pipeline.py --mode daic --daic_root <path> --task regression --epochs 40")
        print("  2. Fine-tune BERT (higher accuracy, needs more GPU memory):")
        print("     Add --freeze_bert 0 --lr 5e-5 to train.py directly")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(
        description="Multimodal Mental Health Analysis — Master Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_pipeline.py                                     # synthetic, quick test
  python run_pipeline.py --mode synthetic --epochs 10        # synthetic, longer
  python run_pipeline.py --mode daic --daic_root C:/data/daic-woz   # real dataset
  python run_pipeline.py --mode eatd --eatd_root ./ICASSP2022-Depression
  python run_pipeline.py --mode evaluate --checkpoint ./backend/checkpoints/daic/best.pt
        """
    )
    p.add_argument("--mode",        default="synthetic",
                   choices=["synthetic", "daic", "eatd", "evaluate"],
                   help="Which dataset/mode to use (default: synthetic)")
    p.add_argument("--daic_root",   default=None,
                   help="Path to DAIC-WOZ root folder")
    p.add_argument("--eatd_root",   default=None,
                   help="Path to EATD-Corpus root folder")
    p.add_argument("--processed_dir", default=None,
                   help="(evaluate mode) path to processed features folder")
    p.add_argument("--checkpoint",  default=None,
                   help="Path to .pt checkpoint (for evaluate mode or eval_only)")
    p.add_argument("--task",        default="classification",
                   choices=["classification", "regression"])
    p.add_argument("--epochs",      type=int,   default=30)
    p.add_argument("--batch_size",  type=int,   default=8)
    p.add_argument("--lr",          type=float, default=2e-4)
    p.add_argument("--quick",       action="store_true",
                   help="Use smaller synthetic dataset (33 participants, fast)")
    p.add_argument("--eval_only",   action="store_true",
                   help="Skip training, only run evaluation")
    p.add_argument("--output_dir",  default="checkpoints",
                   help="Relative path inside backend/ for checkpoints")
    return p.parse_args()


def main():
    args = parse_args()

    banner("Multimodal Mental Health Analysis Pipeline")
    print(f"  Mode       : {args.mode}")
    print(f"  Task       : {args.task}")
    print(f"  Epochs     : {args.epochs}")
    print(f"  Batch size : {args.batch_size}")
    print(f"  GPU        : {'YES' if _has_gpu() else 'NO (CPU mode)'}")
    print(f"  Project    : {PROJECT_ROOT}")

    if args.mode == "synthetic":
        run_synthetic(args)
    elif args.mode == "daic":
        run_daic(args)
    elif args.mode == "eatd":
        run_eatd(args)
    elif args.mode == "evaluate":
        run_evaluate(args)


if __name__ == "__main__":
    main()
