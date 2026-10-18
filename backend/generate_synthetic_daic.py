"""
Synthetic DAIC-WOZ Data Generator
===================================
Generates a fake but structurally identical DAIC-WOZ dataset so you can
develop, debug, and demonstrate the full training pipeline RIGHT NOW —
while waiting for the real dataset approval.

What it creates
---------------
  <output_dir>/
    train_split_Depression_AVEC2017.csv
    dev_split_Depression_AVEC2017.csv
    test_split_Depression_AVEC2017.csv
    train/
      300_P/
        300_AUDIO.wav            (sine-wave audio, 60 s, 16 kHz)
        300_TRANSCRIPT.csv       (realistic interview Q&A)
        300_CLNF_features.txt    (synthetic OpenFace AU sequence)
      ...
    dev/  ...
    test/ ...

The generated data follows the EXACT same file naming, column structure,
and value ranges as the real DAIC-WOZ dataset.  Every script in this
project (clean_daic_dataset.py, dataset.py, train.py, evaluate.py)
will work without modification.

Usage
-----
  python generate_synthetic_daic.py --output_dir ./data/synthetic_daic

  # Then run the full pipeline:
  python clean_daic_dataset.py \\
      --raw_dir ./data/synthetic_daic \\
      --output_dir ./data/synthetic_daic/processed \\
      --split train

  python train.py \\
      --daic_root     ./data/synthetic_daic \\
      --processed_dir ./data/synthetic_daic/processed \\
      --task          classification \\
      --epochs        5 \\
      --batch_size    4 \\
      --output_dir    ./checkpoints/synthetic
"""

import argparse
import random
from pathlib import Path

import numpy as np
import pandas as pd
import soundfile as sf


# ──────────────────────────────────────────────────────────────────────────────
# Dataset size (mirrors real DAIC-WOZ)
# ──────────────────────────────────────────────────────────────────────────────

SPLITS = {
    'train': {'start_id': 300, 'n': 107},
    'dev':   {'start_id': 450, 'n':  35},
    'test':  {'start_id': 492, 'n':  47},
}

# ~29 % of participants are depressed (matches real distribution)
DEPRESSION_RATE = 0.29
SAMPLE_RATE     = 16000
AUDIO_DURATION  = 60          # seconds per synthetic recording
AU_FPS          = 30          # frames per second for AU sequences

# Action Unit column names (17 AUs, intensity _r columns)
AU_COLS = [
    'AU01_r','AU02_r','AU04_r','AU05_r','AU06_r','AU07_r',
    'AU09_r','AU10_r','AU12_r','AU14_r','AU15_r','AU17_r',
    'AU20_r','AU23_r','AU25_r','AU26_r','AU45_r',
]

# Interview questions asked by Ellie (virtual interviewer)
ELLIE_QUESTIONS = [
    "How are you doing today?",
    "Can you tell me a little about yourself?",
    "How have you been sleeping lately?",
    "Do you find yourself enjoying things you used to enjoy?",
    "How is your energy level throughout the day?",
    "Have you been feeling down or hopeless recently?",
    "How is your appetite?",
    "Do you have trouble concentrating?",
    "Have you been feeling more tired than usual?",
    "What do you do to relax or unwind?",
    "Do you have a support system — friends or family you can talk to?",
    "Have you experienced any major stressors recently?",
]

# Responses for non-depressed participants
POSITIVE_RESPONSES = [
    "I'm doing pretty well, thanks for asking.",
    "Things have been going okay. I've been busy but managing.",
    "My sleep has been pretty good lately, usually around seven or eight hours.",
    "Yes, I still enjoy most of my hobbies. I went hiking last weekend.",
    "My energy is generally fine. I feel tired in the evenings but that's normal.",
    "Not really. I feel optimistic about the future.",
    "My appetite is normal. I eat three meals a day.",
    "No major issues with concentration. I can focus well at work.",
    "I feel my normal level of tired, nothing unusual.",
    "I like reading and going for walks. That helps me unwind.",
    "Yes, I have close friends and family I can always turn to.",
    "Not really, things have been relatively stable.",
]

# Responses for depressed participants
NEGATIVE_RESPONSES = [
    "Not great honestly. I've been struggling a lot.",
    "It's been really hard. I feel like I'm just going through the motions.",
    "Terrible. I either can't sleep at all or I sleep way too much.",
    "No. I used to love painting but I can't bring myself to do it anymore.",
    "Very low. I'm exhausted all the time even after resting.",
    "Yeah, I've been feeling pretty hopeless. Nothing seems to get better.",
    "I've been barely eating. Nothing tastes good to me.",
    "It's very hard to focus. My mind just wanders and I can't stay on task.",
    "Constantly tired. Even getting out of bed feels like a huge effort.",
    "I don't really do anything anymore. I just stay home.",
    "I've been isolating myself. I don't really talk to anyone.",
    "There have been a lot of stressors. I feel overwhelmed most of the time.",
]


# ──────────────────────────────────────────────────────────────────────────────
# Audio generator
# ──────────────────────────────────────────────────────────────────────────────

def generate_audio(path: Path, is_depressed: bool, duration: int = AUDIO_DURATION):
    """
    Generate a synthetic audio file.
    Depressed speech: lower pitch, more pauses, quieter.
    Non-depressed:    normal pitch, steady energy.
    """
    n_samples = duration * SAMPLE_RATE
    t = np.linspace(0, duration, n_samples, dtype=np.float32)

    if is_depressed:
        # Lower fundamental frequency (100 Hz), quieter, more silence
        freq      = 100.0 + np.random.uniform(-10, 10)
        amplitude = 0.15 + np.random.uniform(0, 0.1)
        # Introduce random silence gaps (simulates long pauses)
        silence_mask = np.ones(n_samples, dtype=np.float32)
        n_pauses = random.randint(5, 12)
        for _ in range(n_pauses):
            start = random.randint(0, n_samples - SAMPLE_RATE * 3)
            length = random.randint(SAMPLE_RATE, SAMPLE_RATE * 3)
            silence_mask[start:start + length] = 0.0
    else:
        freq      = 150.0 + np.random.uniform(-20, 20)
        amplitude = 0.3 + np.random.uniform(0, 0.15)
        silence_mask = np.ones(n_samples, dtype=np.float32)
        n_pauses = random.randint(1, 4)
        for _ in range(n_pauses):
            start = random.randint(0, n_samples - SAMPLE_RATE)
            length = random.randint(SAMPLE_RATE // 2, SAMPLE_RATE)
            silence_mask[start:start + length] = 0.0

    # Sine wave with harmonics + noise
    audio  = amplitude * np.sin(2 * np.pi * freq * t)
    audio += (amplitude * 0.3) * np.sin(2 * np.pi * freq * 2 * t)
    audio += np.random.normal(0, 0.01, n_samples).astype(np.float32)
    audio *= silence_mask

    # Normalise to [-0.9, 0.9]
    peak = np.max(np.abs(audio)) + 1e-8
    audio = audio / peak * 0.9

    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), audio, SAMPLE_RATE)


# ──────────────────────────────────────────────────────────────────────────────
# Transcript generator
# ──────────────────────────────────────────────────────────────────────────────

def generate_transcript(path: Path, is_depressed: bool):
    """Generate a realistic tab-separated transcript CSV."""
    responses = NEGATIVE_RESPONSES if is_depressed else POSITIVE_RESPONSES
    rows = []
    current_time = 0.0

    for i, question in enumerate(ELLIE_QUESTIONS):
        # Ellie speaks
        q_dur = 2.0 + random.uniform(0, 1.5)
        rows.append({
            'start_time': round(current_time, 2),
            'stop_time':  round(current_time + q_dur, 2),
            'speaker':    'Ellie',
            'value':      question,
        })
        current_time += q_dur + random.uniform(0.3, 0.8)

        # Participant speaks
        response = responses[i % len(responses)]
        # Add slight variation
        if random.random() < 0.3:
            response += " " + random.choice([
                "I don't know.", "It's complicated.", "Yeah.", "I guess so.",
                "Maybe.", "I'm not sure.", "Exactly.", "Definitely."
            ])
        p_dur = 3.0 + len(response.split()) * 0.3 + random.uniform(0, 2)
        if is_depressed:
            p_dur *= 1.4   # depressed speech is slower
        rows.append({
            'start_time': round(current_time, 2),
            'stop_time':  round(current_time + p_dur, 2),
            'speaker':    'Participant',
            'value':      response,
        })
        current_time += p_dur + random.uniform(0.5, 1.5)

    df = pd.DataFrame(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(str(path), sep='\t', index=False)


# ──────────────────────────────────────────────────────────────────────────────
# OpenFace AU feature generator
# ──────────────────────────────────────────────────────────────────────────────

def generate_openface_features(path: Path, is_depressed: bool,
                                duration: int = AUDIO_DURATION):
    """
    Generate synthetic OpenFace CLNF feature file.
    Depressed: lower AU activity, flatter affect (less smile AU12, more AU04).
    Non-depressed: higher AU12 (smile), lower AU04 (brow lowerer).
    """
    n_frames = duration * AU_FPS
    rows = []

    for i in range(n_frames):
        timestamp   = round(i / AU_FPS, 3)
        confidence  = round(np.random.uniform(0.92, 0.99), 4)
        success     = 1

        au_values = {}
        for au in AU_COLS:
            if is_depressed:
                if au == 'AU04_r':   # brow lowerer — higher in depression
                    val = np.random.uniform(0.4, 2.0)
                elif au == 'AU12_r': # lip corner puller (smile) — lower in depression
                    val = np.random.uniform(0.0, 0.3)
                elif au == 'AU15_r': # lip corner depressor — higher in depression
                    val = np.random.uniform(0.2, 1.5)
                elif au == 'AU17_r': # chin raiser — higher in depression
                    val = np.random.uniform(0.2, 1.2)
                else:
                    val = np.random.uniform(0.0, 0.8)
            else:
                if au == 'AU12_r':
                    val = np.random.uniform(0.5, 3.0)
                elif au == 'AU04_r':
                    val = np.random.uniform(0.0, 0.4)
                else:
                    val = np.random.uniform(0.0, 1.5)
            au_values[au] = round(val, 4)

        # Head pose (Tx, Ty, Tz, Rx, Ry, Rz)
        pose = {
            'pose_Tx': round(np.random.normal(0, 5), 3),
            'pose_Ty': round(np.random.normal(0, 5), 3),
            'pose_Tz': round(np.random.normal(600, 20), 3),
            'pose_Rx': round(np.random.normal(0, 0.1), 4),
            'pose_Ry': round(np.random.normal(0, 0.1), 4),
            'pose_Rz': round(np.random.normal(0, 0.05), 4),
        }

        # Gaze
        gaze = {
            'gaze_0_x': round(np.random.normal(0, 0.1), 4),
            'gaze_0_y': round(np.random.normal(0, 0.1), 4),
            'gaze_1_x': round(np.random.normal(0, 0.1), 4),
            'gaze_1_y': round(np.random.normal(0, 0.1), 4),
        }

        row = {'timestamp': timestamp, 'confidence': confidence,
               'success': success}
        row.update(au_values)
        row.update(pose)
        row.update(gaze)
        rows.append(row)

    df = pd.DataFrame(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(str(path), index=False)


# ──────────────────────────────────────────────────────────────────────────────
# Label CSV generator
# ──────────────────────────────────────────────────────────────────────────────

def generate_label_csv(output_dir: Path, split: str,
                       participant_ids: list, labels: list):
    rows = []
    for pid, (phq8, binary, gender) in zip(participant_ids, labels):
        rows.append({
            'Participant_ID': pid,
            'PHQ8_Score':     phq8,
            'PHQ8_Binary':    binary,
            'Gender':         gender,
        })
    df = pd.DataFrame(rows)
    csv_path = output_dir / f'{split}_split_Depression_AVEC2017.csv'
    df.to_csv(str(csv_path), index=False)
    print(f"  Labels saved -> {csv_path}")
    return df


# ──────────────────────────────────────────────────────────────────────────────
# Main generator
# ──────────────────────────────────────────────────────────────────────────────

def generate_split(output_dir: Path, split: str, start_id: int, n: int,
                   audio_duration: int = AUDIO_DURATION):
    print(f"\n[generate] Creating '{split}' split  ({n} participants) …")
    split_dir = output_dir / split
    split_dir.mkdir(parents=True, exist_ok=True)

    participant_ids = list(range(start_id, start_id + n))
    labels = []

    for pid in participant_ids:
        is_depressed = random.random() < DEPRESSION_RATE
        phq8_score   = (
            random.randint(10, 24) if is_depressed
            else random.randint(0, 9)
        )
        gender = random.choice(['Male', 'Female'])
        labels.append((phq8_score, int(is_depressed), gender))

        p_dir = split_dir / f'{pid}_P'
        p_dir.mkdir(parents=True, exist_ok=True)

        # Audio
        generate_audio(p_dir / f'{pid}_AUDIO.wav', is_depressed, audio_duration)

        # Transcript
        generate_transcript(p_dir / f'{pid}_TRANSCRIPT.csv', is_depressed)

        # OpenFace features
        generate_openface_features(
            p_dir / f'{pid}_CLNF_features.txt', is_depressed, audio_duration
        )

        dep_str = 'depressed    ' if is_depressed else 'non-depressed'
        print(f"  [{dep_str}] participant {pid}  PHQ-8={phq8_score}")

    # Label CSV
    generate_label_csv(output_dir, split, participant_ids, labels)
    n_dep = sum(1 for _, b, _ in labels if b == 1)
    print(f"  Done: {n} participants  ({n_dep} depressed, {n - n_dep} non-depressed)")


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(
        description='Generate a synthetic DAIC-WOZ-compatible dataset'
    )
    p.add_argument('--output_dir', default='./data/synthetic_daic',
                   help='Where to write the synthetic dataset (default: ./data/synthetic_daic)')
    p.add_argument('--audio_duration', type=int, default=60,
                   help='Audio length in seconds per participant (default: 60)')
    p.add_argument('--seed', type=int, default=42)
    p.add_argument('--quick', action='store_true',
                   help='Quick mode: 20 train + 8 dev + 5 test participants (for CI/testing)')
    return p.parse_args()


def main():
    args = parse_args()
    random.seed(args.seed)
    np.random.seed(args.seed)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    splits = SPLITS.copy()
    if args.quick:
        splits = {
            'train': {'start_id': 300, 'n': 20},
            'dev':   {'start_id': 400, 'n':  8},
            'test':  {'start_id': 450, 'n':  5},
        }

    print("=" * 60)
    print("  Synthetic DAIC-WOZ Generator")
    print(f"  Output: {output_dir.resolve()}")
    print("=" * 60)

    for split, cfg in splits.items():
        generate_split(
            output_dir,
            split,
            start_id       = cfg['start_id'],
            n              = cfg['n'],
            audio_duration = args.audio_duration,
        )

    print("\n" + "=" * 60)
    print("  Generation complete!")
    print(f"  Dataset root : {output_dir.resolve()}")
    print()
    print("  Next steps:")
    print(f"  1. python clean_daic_dataset.py --raw_dir {args.output_dir} --output_dir {args.output_dir}/processed --split train")
    print(f"  2. python clean_daic_dataset.py --raw_dir {args.output_dir} --output_dir {args.output_dir}/processed --split dev")
    print(f"  3. python train.py --daic_root {args.output_dir} --processed_dir {args.output_dir}/processed --task classification --epochs 5 --batch_size 4 --output_dir ./checkpoints/synthetic")
    print("=" * 60)


if __name__ == '__main__':
    main()
