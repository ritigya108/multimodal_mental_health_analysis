"""
Project Configuration
======================
THE ONLY FILE YOU NEED TO EDIT when switching datasets.

When your DAIC-WOZ access arrives:
  1. Download and extract the dataset
  2. Set DAIC_ROOT and PROCESSED_DIR below
  3. Set DATASET_MODE = "daic"
  4. Run:  python run_pipeline.py
     Everything else works automatically.
"""

from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# CHANGE ONLY THIS SECTION when you get the real dataset
# ─────────────────────────────────────────────────────────────────────────────

# Dataset mode: "synthetic" | "daic" | "eatd"
DATASET_MODE = "synthetic"

# Path to raw DAIC-WOZ root (the folder containing train_split_Depression_AVEC2017.csv)
# Example: DAIC_ROOT = Path("C:/data/daic-woz")
DAIC_ROOT = None

# Path to EATD-Corpus root (only needed if DATASET_MODE = "eatd")
# Example: EATD_ROOT = Path("C:/data/ICASSP2022-Depression")
EATD_ROOT = None

# ─────────────────────────────────────────────────────────────────────────────
# Training hyperparameters — tune these for better results
# ─────────────────────────────────────────────────────────────────────────────

TASK          = "classification"   # "classification" | "regression"
EPOCHS        = 30
BATCH_SIZE    = 8
LEARNING_RATE = 2e-4
EMBED_DIM     = 256                # shared embedding dimension per modality
DROPOUT       = 0.3
FREEZE_BERT   = True               # True = only fine-tune last 2 BERT layers (recommended)
                                   # False = full BERT fine-tune (needs GPU + lower LR ~5e-5)
SEED          = 42

# ─────────────────────────────────────────────────────────────────────────────
# Paths (auto-derived — no need to change these)
# ─────────────────────────────────────────────────────────────────────────────

_HERE = Path(__file__).resolve().parent   # backend/

SYNTHETIC_DIR   = _HERE / "data" / "synthetic_daic"
PROCESSED_DIR   = {
    "synthetic" : SYNTHETIC_DIR / "processed",
    "daic"      : (DAIC_ROOT / "processed") if DAIC_ROOT else None,
    "eatd"      : _HERE / "data" / "eatd_processed",
}
CHECKPOINT_DIR  = _HERE / "checkpoints" / DATASET_MODE


def get_data_paths():
    """
    Returns (daic_root, processed_dir) for the currently configured mode.
    Raises ValueError if required paths are not set.
    """
    if DATASET_MODE == "synthetic":
        return str(SYNTHETIC_DIR), str(PROCESSED_DIR["synthetic"])

    elif DATASET_MODE == "daic":
        if DAIC_ROOT is None:
            raise ValueError(
                "DAIC_ROOT is not set in config.py.\n"
                "Set it to the folder containing train_split_Depression_AVEC2017.csv"
            )
        return str(DAIC_ROOT), str(PROCESSED_DIR["daic"])

    elif DATASET_MODE == "eatd":
        if EATD_ROOT is None:
            raise ValueError(
                "EATD_ROOT is not set in config.py.\n"
                "Set it to the cloned ICASSP2022-Depression folder."
            )
        return str(PROCESSED_DIR["eatd"]), str(PROCESSED_DIR["eatd"])

    else:
        raise ValueError(f"Unknown DATASET_MODE: '{DATASET_MODE}'. "
                         "Choose 'synthetic', 'daic', or 'eatd'.")


# ─────────────────────────────────────────────────────────────────────────────
# Quick self-check when run directly
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Current configuration:")
    print(f"  DATASET_MODE  : {DATASET_MODE}")
    print(f"  TASK          : {TASK}")
    print(f"  EPOCHS        : {EPOCHS}")
    print(f"  BATCH_SIZE    : {BATCH_SIZE}")
    print(f"  LEARNING_RATE : {LEARNING_RATE}")
    print(f"  FREEZE_BERT   : {FREEZE_BERT}")
    print(f"  EMBED_DIM     : {EMBED_DIM}")
    print(f"  DROPOUT       : {DROPOUT}")
    try:
        daic_root, processed_dir = get_data_paths()
        print(f"\n  Dataset root  : {daic_root}")
        print(f"  Processed dir : {processed_dir}")
        print(f"  Checkpoints   : {CHECKPOINT_DIR}")
        print("\n  Config is valid.")
    except ValueError as e:
        print(f"\n  Config issue: {e}")
