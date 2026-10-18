"""
Synthetic Data Preprocessor
=============================
Lightweight preprocessor for synthetic (and any lenient-mode) DAIC-WOZ data.
Bypasses the strict quality checks in clean_daic_dataset.py that reject
synthetic audio, and directly creates the processed features needed by train.py.

Use this instead of clean_daic_dataset.py when working with:
  - Synthetic DAIC data (generate_synthetic_daic.py output)
  - EATD-Corpus (already handled by eatd_adapter.py)
  - Any dataset where audio quality checks are too strict

Usage
-----
  python preprocess_synthetic.py \\
      --raw_dir  ./data/synthetic_daic \\
      --output_dir ./data/synthetic_daic/processed \\
      --split train

  python preprocess_synthetic.py \\
      --raw_dir  ./data/synthetic_daic \\
      --output_dir ./data/synthetic_daic/processed \\
      --split dev
"""

import argparse
import json
import re
from pathlib import Path

import librosa
import numpy as np
import pandas as pd
import soundfile as sf
from scipy.signal import wiener

AU_COLS = [
    'AU01_r','AU02_r','AU04_r','AU05_r','AU06_r','AU07_r',
    'AU09_r','AU10_r','AU12_r','AU14_r','AU15_r','AU17_r',
    'AU20_r','AU23_r','AU25_r','AU26_r','AU45_r',
]


def clean_text(text):
    if pd.isna(text):
        return ""
    fillers = ['um', 'uh', 'like', 'you know', 'i mean', 'sort of', 'kind of']
    for filler in fillers:
        text = re.sub(r'\b' + filler + r'\b', '', str(text), flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    return text.lower().strip()


def extract_audio_features(audio_path: Path) -> dict:
    try:
        audio, sr = librosa.load(str(audio_path), sr=16000)
        features = {}
        mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
        features['mfcc_mean'] = np.mean(mfccs, axis=1)
        features['mfcc_std']  = np.std(mfccs, axis=1)
        pitches, magnitudes   = librosa.piptrack(y=audio, sr=sr)
        pitch_vals = [
            pitches[magnitudes[:, t].argmax(), t]
            for t in range(pitches.shape[1])
            if pitches[magnitudes[:, t].argmax(), t] > 0
        ]
        features['pitch_mean']   = float(np.mean(pitch_vals)) if pitch_vals else 0.0
        features['pitch_std']    = float(np.std(pitch_vals))  if pitch_vals else 0.0
        rms = librosa.feature.rms(y=audio)[0]
        features['energy_mean']  = float(np.mean(rms))
        features['energy_std']   = float(np.std(rms))
        zcr = librosa.feature.zero_crossing_rate(audio)[0]
        features['zcr_mean']     = float(np.mean(zcr))
        features['zcr_std']      = float(np.std(zcr))
        sc = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
        features['spectral_centroid_mean'] = float(np.mean(sc))
        features['spectral_centroid_std']  = float(np.std(sc))
        return features
    except Exception as e:
        print(f"  Warning: audio feature extraction failed: {e}")
        return {}


def process_participant(pid: str, p_dir: Path, output_dir: Path):
    audio_file      = p_dir / f'{pid}_AUDIO.wav'
    transcript_file = p_dir / f'{pid}_TRANSCRIPT.csv'
    openface_file   = p_dir / f'{pid}_CLNF_features.txt'

    # ── Audio ─────────────────────────────────────────────────────────────
    if audio_file.exists():
        features = extract_audio_features(audio_file)
        if features:
            np.save(str(output_dir / 'audio_features' / f'{pid}.npy'), features)
    else:
        print(f"  [{pid}] No audio file found, skipping audio features.")

    # ── Transcript ────────────────────────────────────────────────────────
    if transcript_file.exists():
        try:
            df = pd.read_csv(str(transcript_file), sep='\t')
            if 'speaker' in df.columns and 'value' in df.columns:
                df = df[df['speaker'] == 'Participant'].copy()
                df['text_cleaned'] = df['value'].apply(clean_text)
                df = df[df['text_cleaned'].str.len() > 0]
            elif 'text_cleaned' in df.columns:
                pass  # already cleaned
            df.to_csv(str(output_dir / 'text_features' / f'{pid}.csv'), index=False)
        except Exception as e:
            print(f"  [{pid}] Transcript error: {e}")
    else:
        print(f"  [{pid}] No transcript found, skipping text features.")

    # ── OpenFace AUs ──────────────────────────────────────────────────────
    if openface_file.exists():
        try:
            df = pd.read_csv(str(openface_file))
            df.columns = df.columns.str.strip()
            # Filter confident frames
            if 'confidence' in df.columns and 'success' in df.columns:
                df = df[(df['confidence'] > 0.8) & (df['success'] == 1)]
            avail = [c for c in AU_COLS if c in df.columns]
            if avail:
                feat_cols = ['timestamp'] + avail
                extra = [c for c in ['pose_Tx','pose_Ty','pose_Tz',
                                      'pose_Rx','pose_Ry','pose_Rz',
                                      'gaze_0_x','gaze_0_y',
                                      'gaze_1_x','gaze_1_y'] if c in df.columns]
                feat_cols += extra
                df[feat_cols].to_csv(
                    str(output_dir / 'facial_features' / f'{pid}.csv'), index=False
                )
        except Exception as e:
            print(f"  [{pid}] OpenFace error: {e}")
    else:
        print(f"  [{pid}] No OpenFace file found, skipping facial features.")

    return True


def process_split(raw_dir: Path, output_dir: Path, split: str):
    split_dir = raw_dir / split
    if not split_dir.exists():
        print(f"Split directory not found: {split_dir}")
        return

    # Create output subdirs
    for sub in ['audio_features', 'text_features', 'facial_features']:
        (output_dir / sub).mkdir(parents=True, exist_ok=True)

    folders = [f for f in split_dir.iterdir() if f.is_dir() and f.name.endswith('_P')]
    print(f"\nProcessing {len(folders)} participants from '{split}' split...")

    valid = 0
    for folder in sorted(folders):
        pid = folder.name.split('_')[0]
        print(f"  Processing participant {pid}...")
        if process_participant(pid, folder, output_dir):
            valid += 1

    # Write quality report
    report = {'split': split, 'total': len(folders), 'processed': valid}
    with open(output_dir / f'quality_report_{split}.json', 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\nDone: {valid}/{len(folders)} participants processed.")
    print(f"Output -> {output_dir}")


def parse_args():
    p = argparse.ArgumentParser(description='Preprocess synthetic/lenient DAIC-WOZ data')
    p.add_argument('--raw_dir',    required=True)
    p.add_argument('--output_dir', required=True)
    p.add_argument('--split',      default='train', choices=['train','dev','test'])
    return p.parse_args()


def main():
    args = parse_args()
    process_split(Path(args.raw_dir), Path(args.output_dir), args.split)


if __name__ == '__main__':
    main()
