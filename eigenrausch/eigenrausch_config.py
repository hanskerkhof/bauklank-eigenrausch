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
# We want all layers (BASE, MICRO, PULSE) to render at the same nominal level.
# You can adjust MASTER_OUT_DB to taste (e.g. -10.0, -12.0, -18.0),
# and all layers will follow.

MASTER_OUT_DB = -10.0  # single knob for overall loudness of rendered WAVs

BASE_OUT_DB = MASTER_OUT_DB
MICRO_OUT_DB = MASTER_OUT_DB
PULSE_OUT_DB = MASTER_OUT_DB

# -----------------------------------------------------------------
# Empirical trims to roughly normalize rendered files around -1 dBFS
# (based on your measurements for BASE_A, MICRO_A, PULSE_A):
#
#   BASE_A   ≈ -21 dB  -> +20 dB  -> ~ -1 dB
#   MICRO_A  ≈  -2 dB  ->  +1 dB  -> ~ -1 dB
#   PULSE_A  ≈ -40 dB  -> +39 dB  -> ~ -1 dB
#
# These trims are applied ON TOP of the *_OUT_DB values in each
# synth class. If you re-measure and want to fine-tune, adjust
# ONLY these three numbers.
# -----------------------------------------------------------------
BASE_TRIM_DB = 20.0
MICRO_TRIM_DB = 20.0
PULSE_TRIM_DB = 39.0

def db_to_amp(db: float) -> float:
    """Convert dBFS to linear amplitude factor."""
    return 10 ** (db / 20.0)
