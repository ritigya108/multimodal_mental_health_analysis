"""
Generate professional test audio + video samples for multimodal analysis demo.
Run:  python generate_test_samples.py
Output: test_samples/ folder with 3 audio + 3 video files
"""

import cv2
import numpy as np
import wave
import struct
import math
import os

os.makedirs("test_samples", exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# AUDIO GENERATION
# Produces speech-like WAV files using layered harmonics (sounds like a voice)
# ─────────────────────────────────────────────────────────────────────────────

def make_speech_wav(filename, duration_sec=8, base_freq=180,
                    energy=0.3, jitter=0.0, sample_rate=16000):
    """
    Synthesise a speech-like audio signal using:
    - fundamental frequency (pitch)
    - harmonics (overtones make it sound vocal)
    - amplitude envelope (natural pauses / syllables)
    - jitter (pitch variation — high in anxiety, low in depression)
    """
    n = int(sample_rate * duration_sec)
    t = np.linspace(0, duration_sec, n, endpoint=False)

    signal = np.zeros(n)

    # Fundamental + harmonics
    harmonics = [1, 2, 3, 4, 5]
    harmonic_weights = [1.0, 0.6, 0.35, 0.2, 0.1]
    for h, w in zip(harmonics, harmonic_weights):
        # add small jitter to pitch
        freq_jitter = base_freq * h + jitter * np.random.randn(n) * 2
        phase = np.cumsum(2 * np.pi * freq_jitter / sample_rate)
        signal += w * np.sin(phase)

    # Syllable envelope: bursts of ~200ms every ~350ms
    envelope = np.zeros(n)
    syllable_len  = int(sample_rate * 0.20)
    syllable_gap  = int(sample_rate * 0.35)
    pos = int(sample_rate * 0.3)      # start after 300 ms silence
    while pos + syllable_len < n:
        ramp_up   = np.linspace(0, 1, syllable_len // 4)
        ramp_down = np.linspace(1, 0, syllable_len - len(ramp_up))
        env_chunk = np.concatenate([ramp_up, ramp_down])
        envelope[pos:pos + syllable_len] = env_chunk
        pos += syllable_len + syllable_gap

    signal = signal * envelope * energy

    # Clip and convert to 16-bit PCM
    signal = np.clip(signal * 32767, -32767, 32767).astype(np.int16)

    with wave.open(filename, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(signal.tobytes())
    print(f"  OK Audio: {filename}  ({duration_sec}s, {os.path.getsize(filename)//1024} KB)")


# ─── Audio 1: Depressed — low pitch, very low energy, minimal variation ──────
make_speech_wav(
    "test_samples/audio_depressed_low_energy.wav",
    duration_sec=8,
    base_freq=130,      # low pitch (flat voice)
    energy=0.18,        # very quiet
    jitter=0.5,         # almost no pitch variation
)

# ─── Audio 2: Neutral — normal pitch, medium energy ──────────────────────────
make_speech_wav(
    "test_samples/audio_neutral_normal.wav",
    duration_sec=8,
    base_freq=220,      # normal speaking pitch
    energy=0.45,        # moderate loudness
    jitter=3.0,         # some natural variation
)

# ─── Audio 3: Anxious/Agitated — higher pitch, high energy, lots of jitter ───
make_speech_wav(
    "test_samples/audio_anxious_high_energy.wav",
    duration_sec=8,
    base_freq=290,      # higher pitch (stressed voice)
    energy=0.85,        # loud
    jitter=8.0,         # lots of pitch variation (nervous)
)


# ─────────────────────────────────────────────────────────────────────────────
# VIDEO GENERATION
# Produces an animated face with realistic expressions, blinking, and title card
# ─────────────────────────────────────────────────────────────────────────────

def draw_face(frame, cx, cy, expression="neutral", blink=False,
              skin=(200, 170, 140), frame_idx=0):
    """Draw an animated face onto the frame."""
    h_frame, w_frame = frame.shape[:2]

    # ── Face oval ─────────────────────────────────────────────────────────────
    cv2.ellipse(frame, (cx, cy), (75, 90), 0, 0, 360, skin, -1)
    cv2.ellipse(frame, (cx, cy), (75, 90), 0, 0, 360, (skin[0]-30, skin[1]-30, skin[2]-30), 2)

    # ── Hair ──────────────────────────────────────────────────────────────────
    cv2.ellipse(frame, (cx, cy - 55), (78, 45), 0, 180, 360, (60, 40, 20), -1)

    # ── Eyes ──────────────────────────────────────────────────────────────────
    eye_h = 2 if blink else 10
    for ex in [cx - 26, cx + 26]:
        cv2.ellipse(frame, (ex, cy - 20), (13, eye_h), 0, 0, 360, (50, 35, 20), -1)
        if not blink:
            cv2.circle(frame, (ex, cy - 20), 5, (20, 15, 10), -1)   # pupil
            cv2.circle(frame, (ex - 3, cy - 23), 2, (240, 240, 240), -1)  # highlight

    # ── Eyebrows ──────────────────────────────────────────────────────────────
    if expression == "sad":
        # Brows raised in middle (sad)
        cv2.line(frame, (cx - 38, cy - 40), (cx - 20, cy - 46), (60, 40, 20), 3)
        cv2.line(frame, (cx + 20, cy - 46), (cx + 38, cy - 40), (60, 40, 20), 3)
    elif expression == "anxious":
        # Brows furrowed inward (anxious)
        cv2.line(frame, (cx - 38, cy - 36), (cx - 20, cy - 43), (60, 40, 20), 3)
        cv2.line(frame, (cx + 20, cy - 43), (cx + 38, cy - 36), (60, 40, 20), 3)
    else:
        # Neutral flat brows
        cv2.line(frame, (cx - 38, cy - 38), (cx - 18, cy - 40), (60, 40, 20), 3)
        cv2.line(frame, (cx + 18, cy - 40), (cx + 38, cy - 38), (60, 40, 20), 3)

    # ── Nose ──────────────────────────────────────────────────────────────────
    cv2.ellipse(frame, (cx, cy + 10), (7, 5), 0, 0, 360,
                (skin[0]-25, skin[1]-25, skin[2]-25), 1)

    # ── Mouth ─────────────────────────────────────────────────────────────────
    if expression == "sad":
        # Downward arc
        pts = np.array([[cx - 22, cy + 35], [cx, cy + 44], [cx + 22, cy + 35]], np.int32)
        cv2.polylines(frame, [pts], False, (130, 90, 80), 2)
        # Slight tremble every few frames
        if frame_idx % 12 < 2:
            cv2.ellipse(frame, (cx, cy + 38), (18, 6), 0, 0, 180, (150, 110, 100), 1)
    elif expression == "happy":
        # Upward arc + teeth
        cv2.ellipse(frame, (cx, cy + 28), (22, 14), 0, 180, 360, (130, 90, 80), -1)
        cv2.rectangle(frame, (cx - 18, cy + 28), (cx + 18, cy + 34), (230, 225, 220), -1)
        cv2.ellipse(frame, (cx, cy + 28), (22, 14), 0, 180, 360, (130, 90, 80), 2)
    elif expression == "anxious":
        # Slightly open, tense mouth
        cv2.ellipse(frame, (cx, cy + 32), (16, 8), 0, 0, 360, (130, 90, 80), -1)
        cv2.ellipse(frame, (cx, cy + 32), (16, 8), 0, 0, 360, (100, 70, 60), 2)
    else:
        # Neutral straight line
        cv2.line(frame, (cx - 20, cy + 33), (cx + 20, cy + 33), (130, 90, 80), 2)


def make_video(filename, duration_sec=6, fps=20, expression="neutral",
               bg_color=(45, 45, 55), skin=(200, 170, 140),
               title="", subtitle="", mood_color=(200, 200, 200)):
    """Generate a polished face animation video."""
    W, H = 480, 360
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(filename, fourcc, fps, (W, H))
    n_frames = fps * duration_sec
    cx, cy = W // 2, H // 2 - 20

    blink_frames = set()
    blink_start = fps * 1
    for b in range(0, n_frames, fps * 3):
        blink_frames.update(range(b + fps, b + fps + 3))

    for fi in range(n_frames):
        frame = np.full((H, W, 3), bg_color, dtype=np.uint8)

        # Subtle head sway
        sway = int(3 * math.sin(2 * math.pi * fi / (fps * 2.5)))
        bob  = int(2 * math.sin(2 * math.pi * fi / (fps * 1.8)))

        blink = fi in blink_frames

        draw_face(frame, cx + sway, cy + bob, expression=expression,
                  blink=blink, skin=skin, frame_idx=fi)

        # ── Title bar at bottom ───────────────────────────────────────────────
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, H - 70), (W, H), (20, 20, 20), -1)
        frame = cv2.addWeighted(overlay, 0.75, frame, 0.25, 0)

        cv2.putText(frame, title,    (16, H - 44), cv2.FONT_HERSHEY_DUPLEX,
                    0.65, mood_color, 1, cv2.LINE_AA)
        cv2.putText(frame, subtitle, (16, H - 18), cv2.FONT_HERSHEY_SIMPLEX,
                    0.45, (170, 170, 170), 1, cv2.LINE_AA)

        # ── "DEMO" watermark ─────────────────────────────────────────────────
        cv2.putText(frame, "DEMO", (W - 70, 24), cv2.FONT_HERSHEY_SIMPLEX,
                    0.55, (80, 80, 80), 1, cv2.LINE_AA)

        out.write(frame)

    out.release()
    print(f"  OK Video: {filename}  ({duration_sec}s, {os.path.getsize(filename)//1024} KB)")


# ─── Video 1: Depressed — pale face, sad expression, dark background ─────────
make_video(
    "test_samples/video_depressed_expression.mp4",
    duration_sec=6, fps=20,
    expression="sad",
    bg_color=(25, 25, 30),
    skin=(155, 148, 140),       # pale / washed-out skin
    title="Low Affect — Depressed Expression",
    subtitle="Flat affect, downturned mouth, minimal movement",
    mood_color=(100, 140, 220),
)

# ─── Video 2: Neutral — normal expression, neutral background ────────────────
make_video(
    "test_samples/video_neutral_expression.mp4",
    duration_sec=6, fps=20,
    expression="neutral",
    bg_color=(45, 45, 55),
    skin=(195, 162, 128),
    title="Neutral Expression",
    subtitle="Normal affect, resting face, regular blinking",
    mood_color=(200, 200, 200),
)

# ─── Video 3: Positive — warm tones, happy expression ────────────────────────
make_video(
    "test_samples/video_positive_expression.mp4",
    duration_sec=6, fps=20,
    expression="happy",
    bg_color=(35, 50, 35),
    skin=(210, 175, 135),
    title="Positive Affect — Happy Expression",
    subtitle="Smile, bright eyes, warm skin tone",
    mood_color=(100, 210, 130),
)


# ─────────────────────────────────────────────────────────────────────────────
print()
print("=" * 55)
print("  TEST SAMPLES READY  →  test_samples/")
print("=" * 55)
import os
files = sorted(os.listdir("test_samples"))
for f in files:
    size = os.path.getsize(f"test_samples/{f}") // 1024
    print(f"  {f:<45} {size:>5} KB")
print("=" * 55)
