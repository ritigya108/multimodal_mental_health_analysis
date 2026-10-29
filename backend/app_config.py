"""
app_config.py — Application-level configuration (not ML/dataset config).

Edit CRISIS_HELPLINE_NUMBER and CRISIS_HELPLINE_NAME to match the target
country/region before deploying.
"""

# ── Crisis helpline (configurable) ────────────────────────────────────────────
# India: Tele-MANAS (Ministry of Health) — free, 24/7, multilingual
CRISIS_HELPLINE_NUMBER: str = "14416"
CRISIS_HELPLINE_NAME: str = "Tele-MANAS"
CRISIS_HELPLINE_DESCRIPTION: str = "Free 24/7 mental health support (India)"

# File size limits for uploaded media
MAX_AUDIO_SIZE_MB: int = 50
MAX_VIDEO_SIZE_MB: int = 200

# Assessment history pagination
ASSESSMENT_PAGE_SIZE: int = 5

# Data retention note (shown in Settings)
DATA_RETENTION_NOTE: str = (
    "Uploaded audio and video files are deleted immediately after feature "
    "extraction. Text transcripts and derived features are retained until "
    "you request deletion via Settings."
)
