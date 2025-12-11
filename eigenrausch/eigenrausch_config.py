"""
eigenrausch_config.py

Shared configuration for Eigenrausch layers.
"""

from pathlib import Path

# =========================================================
# AUDIO / RENDER SETTINGS
# =========================================================

SAMPLE_RATE = 48000          # Hz. 48000 is a good compromise.
DURATION_MIN = 0.05          # Length of rendered files in minutes (use small for tests).
DURATION_SEC = DURATION_MIN * 60

# Output directories for rendered WAVs.
OUTPUT_DIR_BASE = Path("eigenrausch_base")
OUTPUT_DIR_MICRO = Path("eigenrausch_micro")
OUTPUT_DIR_PULSE = Path("eigenrausch_pulse")

for directory in (OUTPUT_DIR_BASE, OUTPUT_DIR_MICRO, OUTPUT_DIR_PULSE):
    directory.mkdir(exist_ok=True)

# Master output levels in dBFS.
# For testing on laptop speakers, -10 dB is loud-ish.
# For final stems, you can go lower (e.g. -30 to -40 dB).
BASE_OUT_DB = -10.0
MICRO_OUT_DB = -5.0    # micro layer fairly audible for testing
PULSE_OUT_DB = -2.0    # pulse layer level


def db_to_amp(db: float) -> float:
    """Convert dBFS to linear amplitude factor."""
    return 10 ** (db / 20.0)
