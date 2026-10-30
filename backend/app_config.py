"""
app_config.py — Application-level configuration (not ML/dataset config).

Edit CRISIS_HELPLINE_NUMBER and CRISIS_HELPLINE_NAME to match the target
country/region before deploying.  These values can also be overridden via
the CRISIS_HELPLINE_NUMBER and CRISIS_HELPLINE_NAME environment variables.
"""

import os

# ── Crisis helpline (configurable) ────────────────────────────────────────────
# India: Tele-MANAS (Ministry of Health) — free, 24/7, multilingual
CRISIS_HELPLINE_NUMBER: str = os.environ.get("CRISIS_HELPLINE_NUMBER", "14416")
CRISIS_HELPLINE_NAME: str = os.environ.get("CRISIS_HELPLINE_NAME", "Tele-MANAS")
CRISIS_HELPLINE_DESCRIPTION: str = "Free 24/7 mental health support (India)"

# File size limit for uploaded audio
MAX_AUDIO_SIZE_MB: int = 50

# Assessment history pagination
ASSESSMENT_PAGE_SIZE: int = 5

# Data retention note (shown in Settings)
DATA_RETENTION_NOTE: str = (
    "Uploaded audio files are deleted immediately after feature extraction. "
    "Text transcripts and derived features are retained until "
    "you request deletion via Settings."
)
