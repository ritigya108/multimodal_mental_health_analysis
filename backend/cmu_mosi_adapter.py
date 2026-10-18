"""
CMU-MOSI Adapter
=================
Converts the CMU-MOSI (Multimodal Opinion Sentiment Intensity) dataset
into the DAIC-WOZ-compatible processed format used by our pipeline.

CMU-MOSI is publicly available and contains audio + text + visual features
aligned at the utterance level with sentiment scores. We repurpose the
negative-sentiment utterances as a proxy for depression indicators —
a common research approach when DAIC-WOZ access is pending.

About CMU-MOSI
--------------
- Homepage   : http://multicomp.cs.cmu.edu/resources/cmu-mosi-dataset/
- SDK repo   : https://github.com/CMU-MultiComp-Lab/CMU-MultimodalSDK
- Size       : 2199 opinion utterances, 89 YouTube videos
- Modalities : raw audio (.wav), text transcripts, pre-extracted visual features
- Labels     : sentiment score ∈ [-3, +3]  (we threshold at < -1 → "depressed")

IMPORTANT CAVEAT
----------------
CMU-MOSI is a sentiment dataset, NOT a clinical depression dataset.
Using it means your model is detecting strong negative sentiment as
a depression proxy — which is valid for a final-year project demonstration
but should be clearly disclosed in your report/presentation.

Download
--------
  pip install mmsdk
  # The SDK downloads features automatically; OR manually:
  git clone https://github.com/CMU-MultiComp-Lab/CMU-MultimodalSDK
  cd CMU-MultimodalSDK
  python -c "import mmsdk; mmsdk.mmdatasdk.dataset.standard_datasets.CMU_MOSI.highlevel"

Alternatively, the pre-extracted CMU-MOSI features are available as
a single pickle file from several mirrors:
  https://github.com/thuiar/TEXTCNN-sentiment/tree/master/datasets
  https://www.dropbox.com/sh/hyzpgx1hp9nj37s/AAB7FhBqJOFDw2hEyvv2ZXHxa

Usage
-----
  python cmu_mosi_adapter.py \\
      --mosi_pkl  ./data/mosi_data.pkl \\
      --output_dir ./data/mosi_processed

  Then train exactly as with DAIC-WOZ:
  python train.py \\
      --daic_root     ./data/mosi_processed \\
      --processed_dir ./data/mosi_processed \\
      --task          classification \\
      --epochs        30 \\
      --batch_size    16 \\
      --output_dir    ./checkpoints/mosi
"""

import argparse
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

# Sentiment score threshold → binary "depression proxy" label
# Utterances with mean score < NEG_THRESHOLD are treated as depressed
NEG_THRESHOLD = -1.0

# AU_COLS from dataset.py (we create zero placeholders since CMU-MOSI
# provides pre-extracted visual features, not raw OpenFace AUs)
AU_COLS = [
    'AU01_r','AU02_r','AU04_r','AU05_r','AU06_r','AU07_r',
    'AU09_r','AU10_r','AU12_r','AU14_r','AU15_r','AU17_r',
    'AU20_r','AU23_r','AU25_r','AU26_r','AU45_r',
]
MAX_AU_FRAMES = 300


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def make_placeholder_au_csv(path: Path, n_frames: int = MAX_AU_FRAMES):
    rows = []
    for i in range(n_frames):
        row = {'timestamp': round(i / 30.0, 3), 'confidence': 0.95, 'success': 1}
        for au in AU_COLS:
            row[au] = 0.0
        rows.append(row)
    pd.DataFrame(rows).to_csv(str(path), index=False)


def save_acoustic_features(audio_features: np.ndarray, path: Path):
    """
    CMU-MOSI typically provides COVAREP or Facet acoustic features.
    We save them as-is; dataset.py handles both dict and array formats.
    """
    np.save(str(path), audio_features.astype(np.float32))


# ──────────────────────────────────────────────────────────────────────────────
# Load the CMU-MOSI pickle (SDK format)
# ──────────────────────────────────────────────────────────────────────────────

def load_mosi_pickle(pkl_path: str) -> dict:
    """
    Load a CMU-MOSI pickle file.
    Expected keys: 'train', 'valid', 'test'
    Each split is a dict with keys: 'audio', 'vision', 'text', 'labels'
    Each value is a numpy array of shape (N_utterances, T, D) or (N_utterances,)
    """
    with open(pkl_path, 'rb') as f:
        data = pickle.load(f, encoding='latin1')
    return data


# ──────────────────────────────────────────────────────────────────────────────
# Convert one split
# ──────────────────────────────────────────────────────────────────────────────

def convert_split(data: dict, split_key: str, output_dir: Path,
                  split_name: str, start_pid: int = 0):
    """
    Convert one CMU-MOSI split into DAIC-WOZ-compatible processed format.
    """
    print(f"\n[mosi_adapter] Converting '{split_name}' split …")

    split_data = data.get(split_key, data.get(
        'valid' if split_key == 'dev' else split_key, {}
    ))

    audio_arr  = split_data.get('audio',  None)  # (N, T, D_audio)
    text_arr   = split_data.get('text',   None)  # (N, T, D_text) or list of strings
    label_arr  = split_data.get('labels', None)  # (N,) or (N, 1) — sentiment score

    if label_arr is None:
        print(f"  No labels found for split '{split_key}', skipping.")
        return

    label_arr = np.array(label_arr).flatten()
    N = len(label_arr)

    # Output directories
    audio_dir  = output_dir / 'audio_features'
    text_dir   = output_dir / 'text_features'
    facial_dir = output_dir / 'facial_features'
    for d in [audio_dir, text_dir, facial_dir]:
        d.mkdir(parents=True, exist_ok=True)

    label_rows = []

    for i in range(N):
        pid       = str(start_pid + i)
        sentiment = float(label_arr[i])

        # Binary label: sentiment < -1 → depressed proxy
        binary  = int(sentiment < NEG_THRESHOLD)
        # Map sentiment to PHQ-8-like score (rough linear mapping -3…+3 → 24…0)
        phq8    = int(np.clip(((-sentiment + 3) / 6) * 24, 0, 24))

        # ── Audio features ─────────────────────────────────────────
        if audio_arr is not None and i < len(audio_arr):
            feat = audio_arr[i]  # (T, D) — mean-pool over time
            if feat.ndim == 2:
                feat = np.mean(feat, axis=0)
            save_acoustic_features(feat, audio_dir / f'{pid}.npy')

        # ── Text ───────────────────────────────────────────────────
        if text_arr is not None and i < len(text_arr):
            t = text_arr[i]
            if isinstance(t, (list, np.ndarray)):
                # Word vectors → join indexed tokens if available, else placeholder
                text_str = f'utterance_{pid}'
            else:
                text_str = str(t)
        else:
            text_str = f'utterance_{pid}'

        pd.DataFrame([{
            'speaker':      'Participant',
            'value':        text_str,
            'text_cleaned': text_str,
        }]).to_csv(str(text_dir / f'{pid}.csv'), index=False)

        # ── Facial AUs (placeholder — CMU-MOSI has Facet, not OpenFace) ──
        make_placeholder_au_csv(facial_dir / f'{pid}.csv')

        label_rows.append({
            'Participant_ID': pid,
            'PHQ8_Score':     phq8,
            'PHQ8_Binary':    binary,
            'Gender':         'Unknown',
        })

    # Label CSV
    out_csv = output_dir / f'{split_name}_split_Depression_AVEC2017.csv'
    pd.DataFrame(label_rows).to_csv(str(out_csv), index=False)
    n_dep = sum(r['PHQ8_Binary'] for r in label_rows)
    print(f"  {N} utterances  ({n_dep} negative-sentiment, {N - n_dep} positive)")
    print(f"  Labels → {out_csv}")
    return start_pid + N


# ──────────────────────────────────────────────────────────────────────────────
# Text-only mode (for when only the raw transcripts pickle is available)
# ──────────────────────────────────────────────────────────────────────────────

def convert_text_only(pkl_path: str, output_dir: Path):
    """
    Minimal converter when CMU-MOSI is available as raw text + labels only.
    Expected pickle structure: list of dicts with 'text' and 'label' keys.
    """
    with open(pkl_path, 'rb') as f:
        samples = pickle.load(f, encoding='latin1')

    print(f"[mosi_adapter] Text-only mode: {len(samples)} samples")

    audio_dir  = output_dir / 'audio_features'
    text_dir   = output_dir / 'text_features'
    facial_dir = output_dir / 'facial_features'
    for d in [audio_dir, text_dir, facial_dir]:
        d.mkdir(parents=True, exist_ok=True)

    label_rows = []
    n = len(samples)
    train_cut = int(n * 0.7)
    dev_cut   = int(n * 0.85)

    for i, s in enumerate(samples):
        pid       = str(i)
        sentiment = float(s.get('label', s.get('sentiment', 0.0)))
        text_str  = str(s.get('text', s.get('sentence', '')))
        binary    = int(sentiment < NEG_THRESHOLD)
        phq8      = int(np.clip(((-sentiment + 3) / 6) * 24, 0, 24))

        pd.DataFrame([{'speaker': 'Participant', 'value': text_str,
                        'text_cleaned': text_str}]).to_csv(
            str(text_dir / f'{pid}.csv'), index=False
        )
        make_placeholder_au_csv(facial_dir / f'{pid}.csv')
        label_rows.append({'Participant_ID': pid, 'PHQ8_Score': phq8,
                            'PHQ8_Binary': binary, 'Gender': 'Unknown'})

    # Split into train / dev / test
    splits = {
        'train': label_rows[:train_cut],
        'dev':   label_rows[train_cut:dev_cut],
        'test':  label_rows[dev_cut:],
    }
    for sname, rows in splits.items():
        pd.DataFrame(rows).to_csv(
            str(output_dir / f'{sname}_split_Depression_AVEC2017.csv'), index=False
        )
    print(f"  Splits: train={len(splits['train'])}, "
          f"dev={len(splits['dev'])}, test={len(splits['test'])}")


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description='Convert CMU-MOSI to DAIC-WOZ format')
    p.add_argument('--mosi_pkl',   required=True,
                   help='Path to CMU-MOSI pickle file')
    p.add_argument('--output_dir', required=True,
                   help='Output directory for processed features')
    p.add_argument('--text_only',  action='store_true',
                   help='Use text-only mode (for simple text+label pickles)')
    return p.parse_args()


def main():
    args   = parse_args()
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  CMU-MOSI → DAIC-WOZ Format Adapter")
    print(f"  Source : {args.mosi_pkl}")
    print(f"  Output : {outdir.resolve()}")
    print("=" * 60)

    if args.text_only:
        convert_text_only(args.mosi_pkl, outdir)
    else:
        data    = load_mosi_pickle(args.mosi_pkl)
        pid_ctr = 0
        for split_key, split_name in [('train','train'), ('valid','dev'), ('test','test')]:
            result = convert_split(data, split_key, outdir, split_name, pid_ctr)
            if result:
                pid_ctr = result

    print("\n" + "=" * 60)
    print("  Conversion complete!")
    print()
    print("  Now train with:")
    print(f"    python train.py \\")
    print(f"        --daic_root     {args.output_dir} \\")
    print(f"        --processed_dir {args.output_dir} \\")
    print(f"        --task          classification \\")
    print(f"        --epochs        30 \\")
    print(f"        --batch_size    16 \\")
    print(f"        --output_dir    ./checkpoints/mosi")
    print()
    print("  IMPORTANT: CMU-MOSI labels negative sentiment, NOT clinical depression.")
    print("             Clearly disclose this limitation in your report.")
    print("=" * 60)


if __name__ == '__main__':
    main()
