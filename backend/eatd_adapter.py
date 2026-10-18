"""
EATD-Corpus Adapter
====================
Converts the EATD-Corpus into the same processed format used by our pipeline.

Real EATD-Corpus folder layout (after downloading from OneDrive)
-----------------------------------------------------------------
  <eatd_root>/
    ├── train/
    │   ├── <participant_folder>/
    │   │   ├── positive.wav          (or positive_out.wav)
    │   │   ├── negative.wav          (or negative_out.wav)
    │   │   ├── neutral.wav           (or neutral_out.wav)
    │   │   ├── positive.txt
    │   │   ├── negative.txt
    │   │   ├── neutral.txt
    │   │   ├── label.txt             (raw SDS score)
    │   │   └── new_label.txt         (SDS × 1.25)
    │   └── ...
    └── validation/    (or val/ or test/)
        └── ...

Download the dataset
--------------------
  1. Go to: https://1drv.ms/u/s!AsGVGqImbOwYhHUHcodFC3xmKZKK?e=mCT5oN
  2. Password: Ymj26Uv5
  3. Extract the ZIP — you'll get a folder with train/ and validation/ inside
  4. Run this script pointing --eatd_root at that extracted folder

Usage
-----
  python eatd_adapter.py ^
      --eatd_root  C:\\Users\\HP\\EATD-Corpus ^
      --output_dir C:\\Users\\HP\\.bob\\playground\\multimodal_mental_health_analysis\\backend\\data\\eatd_processed

  Then train:
  python train.py ^
      --daic_root     .\\data\\eatd_processed ^
      --processed_dir .\\data\\eatd_processed ^
      --task          classification ^
      --epochs        30 ^
      --batch_size    8 ^
      --output_dir    .\\checkpoints\\eatd ^
      --no_cuda
"""

import argparse
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import librosa
import soundfile as sf

import sys
sys.path.insert(0, str(Path(__file__).parent))
from dataset import AU_COLS, MAX_AU_FRAMES, N_MELS, SAMPLE_RATE


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _find_split_dir(root: Path, candidates: list) -> Path:
    """Return the first existing subfolder from a list of candidate names."""
    for name in candidates:
        p = root / name
        if p.exists() and p.is_dir():
            return p
    return None


def _read_sds_label(participant_dir: Path) -> float:
    """
    Read SDS score from new_label.txt (preferred) or label.txt.
    Returns the numeric score, or None if not found.
    """
    for fname in ['new_label.txt', 'label.txt']:
        f = participant_dir / fname
        if f.exists():
            try:
                text = f.read_text(encoding='utf-8').strip()
                # file may contain just the number or "SDS: 53" etc.
                for token in text.replace('\n', ' ').split():
                    try:
                        return float(token)
                    except ValueError:
                        continue
            except Exception:
                pass
    return None


def concatenate_wav_files(wav_paths: list, output_path: Path):
    """Merge multiple wav files into one continuous recording."""
    combined = np.array([], dtype=np.float32)
    for wp in sorted(wav_paths):
        try:
            audio, _ = librosa.load(str(wp), sr=SAMPLE_RATE)
            combined = np.concatenate([combined, audio,
                                       np.zeros(int(SAMPLE_RATE * 0.3), dtype=np.float32)])
        except Exception as e:
            print(f"    Warning: could not load {wp.name}: {e}")
    if len(combined) == 0:
        combined = np.zeros(SAMPLE_RATE * 5, dtype=np.float32)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(output_path), combined, SAMPLE_RATE)


def extract_audio_features(audio_path: Path) -> dict:
    """Extract MFCC + prosodic features."""
    try:
        audio, sr = librosa.load(str(audio_path), sr=SAMPLE_RATE)
        features = {}
        mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
        features['mfcc_mean'] = np.mean(mfccs, axis=1)
        features['mfcc_std']  = np.std(mfccs,  axis=1)
        pitches, mags = librosa.piptrack(y=audio, sr=sr)
        pitch_vals = [pitches[mags[:, t].argmax(), t]
                      for t in range(pitches.shape[1])
                      if pitches[mags[:, t].argmax(), t] > 0]
        features['pitch_mean']  = float(np.mean(pitch_vals)) if pitch_vals else 0.0
        features['pitch_std']   = float(np.std(pitch_vals))  if pitch_vals else 0.0
        rms = librosa.feature.rms(y=audio)[0]
        features['energy_mean'] = float(np.mean(rms))
        features['energy_std']  = float(np.std(rms))
        zcr = librosa.feature.zero_crossing_rate(audio)[0]
        features['zcr_mean']    = float(np.mean(zcr))
        features['zcr_std']     = float(np.std(zcr))
        sc = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
        features['spectral_centroid_mean'] = float(np.mean(sc))
        features['spectral_centroid_std']  = float(np.std(sc))
        return features
    except Exception as e:
        print(f"    Warning: feature extraction failed: {e}")
        return {}


def make_empty_au_csv(path: Path):
    """Placeholder AU CSV (all zeros) — EATD has no video."""
    rows = [{'timestamp': round(i / 30.0, 3), 'confidence': 0.95, 'success': 1,
             **{au: 0.0 for au in AU_COLS}}
            for i in range(MAX_AU_FRAMES)]
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(str(path), index=False)


# ──────────────────────────────────────────────────────────────────────────────
# Core conversion
# ──────────────────────────────────────────────────────────────────────────────

# SDS depression threshold (raw score × 1.25).
# Standard cut-off: SDS ≥ 53 = depressed (raw ≥ 42.4)
SDS_THRESHOLD = 53.0


def convert_split(split_dir: Path, output_dir: Path, split_name: str):
    """
    Process one split (train / validation) and write:
      - output_dir/audio_features/<pid>.npy
      - output_dir/text_features/<pid>.csv
      - output_dir/facial_features/<pid>.csv
      - output_dir/<split_name>_split_Depression_AVEC2017.csv
    """
    print(f"\n[eatd_adapter] Converting '{split_name}' split from: {split_dir}")

    if not split_dir.exists():
        print(f"  ERROR: folder not found: {split_dir}")
        return

    audio_dir  = output_dir / 'audio_features'
    text_dir   = output_dir / 'text_features'
    facial_dir = output_dir / 'facial_features'
    audio_wav  = output_dir / 'processed_audio'
    for d in [audio_dir, text_dir, facial_dir, audio_wav]:
        d.mkdir(parents=True, exist_ok=True)

    participant_dirs = sorted([p for p in split_dir.iterdir() if p.is_dir()])
    if not participant_dirs:
        print(f"  ERROR: no participant folders found inside {split_dir}")
        return

    label_rows = []
    processed  = 0
    skipped    = 0

    for p_dir in participant_dirs:
        pid = p_dir.name

        # ── Read SDS label ────────────────────────────────────────────────
        sds_score = _read_sds_label(p_dir)
        if sds_score is None:
            print(f"  Skipping {pid}: no label file found")
            skipped += 1
            continue

        # SDS ≥ 53 -> depressed
        binary_label = 1 if sds_score >= SDS_THRESHOLD else 0
        # Map to PHQ-8 range (0–24) for regression compatibility
        phq8_estimate = round((sds_score / 80.0) * 24.0, 1)  # SDS max ≈ 80
        phq8_estimate = min(24.0, max(0.0, phq8_estimate))

        # ── Audio: prefer *_out.wav (preprocessed), fall back to *.wav ───
        wav_files = []
        for emotion in ['positive', 'negative', 'neutral']:
            for suffix in [f'{emotion}_out.wav', f'{emotion}.wav']:
                wf = p_dir / suffix
                if wf.exists():
                    wav_files.append(wf)
                    break

        if wav_files:
            merged = audio_wav / f'{pid}.wav'
            concatenate_wav_files(wav_files, merged)
            feats = extract_audio_features(merged)
            if feats:
                np.save(str(audio_dir / f'{pid}.npy'), feats)
        else:
            print(f"  Warning: no wav files for {pid}")

        # ── Text: merge positive/negative/neutral .txt ────────────────────
        utterances = []
        for emotion in ['positive', 'negative', 'neutral']:
            tf = p_dir / f'{emotion}.txt'
            if tf.exists():
                try:
                    text = tf.read_text(encoding='utf-8', errors='ignore').strip()
                    if text:
                        utterances.append({
                            'speaker': 'Participant',
                            'value': text,
                            'text_cleaned': text,
                            'emotion': emotion,
                        })
                except Exception as e:
                    print(f"    Warning: could not read {tf.name}: {e}")

        if utterances:
            pd.DataFrame(utterances).to_csv(
                str(text_dir / f'{pid}.csv'), index=False
            )
        else:
            # Write empty placeholder so dataset.py doesn't skip this participant
            pd.DataFrame([{'speaker': 'Participant', 'value': '', 'text_cleaned': ''}]
                         ).to_csv(str(text_dir / f'{pid}.csv'), index=False)

        # ── Facial: EATD has no video -> zero placeholder ──────────────────
        make_empty_au_csv(facial_dir / f'{pid}.csv')

        label_rows.append({
            'Participant_ID': pid,
            'PHQ8_Score':     phq8_estimate,
            'PHQ8_Binary':    binary_label,
            'Gender':         'Unknown',
        })
        processed += 1

    if not label_rows:
        print(f"  ERROR: no participants processed for split '{split_name}'.")
        print(f"         Make sure you downloaded the actual data files from OneDrive,")
        print(f"         not just the GitHub code repository.")
        return

    # Write DAIC-WOZ-format label CSV
    out_csv = output_dir / f'{split_name}_split_Depression_AVEC2017.csv'
    pd.DataFrame(label_rows).to_csv(str(out_csv), index=False)

    n_dep = sum(1 for r in label_rows if r['PHQ8_Binary'] == 1)
    print(f"  Done: {processed} participants  "
          f"({n_dep} depressed / {processed - n_dep} non-depressed)  "
          f"[{skipped} skipped]")
    print(f"  Labels -> {out_csv}")


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(
        description='Convert EATD-Corpus to DAIC-WOZ pipeline format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Download the EATD dataset first:
  1. Open: https://1drv.ms/u/s!AsGVGqImbOwYhHUHcodFC3xmKZKK?e=mCT5oN
  2. Password: Ymj26Uv5
  3. Extract the ZIP — you will get a folder with train/ and validation/ subfolders

Then run:
  python eatd_adapter.py ^
      --eatd_root  C:\\Users\\HP\\EATD-Corpus ^
      --output_dir .\\data\\eatd_processed
        """
    )
    p.add_argument('--eatd_root',  required=True,
                   help='Extracted EATD-Corpus folder (contains train/ and validation/)')
    p.add_argument('--output_dir', required=True,
                   help='Where to write processed features and label CSVs')
    return p.parse_args()


def main():
    args  = parse_args()
    root  = Path(args.eatd_root)
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  EATD-Corpus -> DAIC-WOZ Format Adapter")
    print(f"  Source : {root.resolve()}")
    print(f"  Output : {outdir.resolve()}")
    print("=" * 60)

    # ── Detect folder layout ──────────────────────────────────────────────
    # Layout A: root/train/ + root/validation/   (split already done)
    # Layout B: root/EATD-Corpus/t_1/ t_2/ ...  (single flat folder — split manually)
    # Layout C: root/t_1/ t_2/ ...               (flat at root level)

    train_dir = _find_split_dir(root, ['train', 'Train', 'new_train', 'TRAIN'])

    if train_dir is None:
        # Try one level deeper (zip extracted as root/EATD-Corpus/t_1/...)
        inner = _find_split_dir(root, ['EATD-Corpus', 'eatd-corpus', 'EATD_Corpus'])
        if inner:
            # Check if inner has train/ subfolders
            train_dir = _find_split_dir(inner, ['train', 'Train', 'new_train'])
            if train_dir is None:
                # Flat layout inside inner folder — split manually
                root = inner

        if train_dir is None:
            # Flat layout: all participants directly in root (t_1, t_2, ...)
            participant_dirs = sorted([p for p in root.iterdir()
                                       if p.is_dir() and not p.name.startswith('.')])
            if participant_dirs:
                print(f"\nDetected flat layout — {len(participant_dirs)} participants, splitting 80/20 train/dev")
                split_idx = int(len(participant_dirs) * 0.8)
                train_participants = participant_dirs[:split_idx]
                dev_participants   = participant_dirs[split_idx:]

                # Create temp split dirs
                import tempfile, shutil as _shutil
                tmp = Path(tempfile.mkdtemp())
                tmp_train = tmp / 'train'
                tmp_dev   = tmp / 'validation'
                tmp_train.mkdir(); tmp_dev.mkdir()

                for p in train_participants:
                    _shutil.copytree(str(p), str(tmp_train / p.name))
                for p in dev_participants:
                    _shutil.copytree(str(p), str(tmp_dev / p.name))

                train_dir = tmp_train
                dev_dir   = tmp_dev
            else:
                print("\nERROR: Could not find participant folders inside:", root)
                print("Subfolders found:")
                for f in root.iterdir():
                    print(f"  {f.name}/")
                raise SystemExit(1)
        else:
            dev_dir = _find_split_dir(inner, ['validation', 'val', 'dev', 'test',
                                               'Validation', 'Val', 'Dev', 'Test'])
            if dev_dir is None:
                dev_dir = train_dir
    else:
        dev_dir = _find_split_dir(root, ['validation', 'val', 'dev', 'test',
                                          'Validation', 'Val', 'Dev', 'Test', 'new_test'])
        if dev_dir is None:
            print("Warning: no validation folder found — using train split as dev too.")
            dev_dir = train_dir

    convert_split(train_dir, outdir, 'train')
    convert_split(dev_dir,   outdir, 'dev')

    # Copy dev as test so evaluate.py --split test also works
    dev_csv  = outdir / 'dev_split_Depression_AVEC2017.csv'
    test_csv = outdir / 'test_split_Depression_AVEC2017.csv'
    if dev_csv.exists():
        shutil.copy(str(dev_csv), str(test_csv))

    print("\n" + "=" * 60)
    print("  Conversion complete!")
    print()
    print("  Now run training:")
    print()
    print(f"  python train.py ^")
    print(f"      --daic_root     {args.output_dir} ^")
    print(f"      --processed_dir {args.output_dir} ^")
    print(f"      --task          classification ^")
    print(f"      --epochs        30 ^")
    print(f"      --batch_size    8 ^")
    print(f"      --output_dir    .\\checkpoints\\eatd ^")
    print(f"      --no_cuda")
    print("=" * 60)


if __name__ == '__main__':
    main()
