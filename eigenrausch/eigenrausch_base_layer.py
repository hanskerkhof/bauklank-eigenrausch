"""
eigenrausch_base_layer.py

Eigenrausch BASE layer:
- eigengrau-style band-limited noise
- slow spectral drift
- slow amplitude "breathing"
"""

import time
from typing import Optional

from pyo import (
    Server,
    PinkNoise,
    Sine,
    ButBP,
    pa_get_default_output,
)

from eigenrausch_config import (
    SAMPLE_RATE,
    DURATION_SEC,
    OUTPUT_DIR_BASE,
    BASE_OUT_DB,
    BASE_TRIM_DB,
    db_to_amp,
)


# ---------------------------------------------------------
# BASE variant definitions
# ---------------------------------------------------------

# BASE_VARIANTS = {
#     # Fairly mid-focused, gentle drift.
#     "BASE_A": {
#         "center_freq_hz": 2800.0,
#         "drift_depth_hz": 300.0,
#         "drift_period_sec": 5 * 60.0,  # 5 minutes per drift cycle
#         "amp_lfo_depth": 0.2,          # ±20% amplitude variation
#         "amp_lfo_period_sec": 3 * 60.0,
#     },
#     # Slightly brighter variant.
#     "BASE_B": {
#         "center_freq_hz": 3200.0,
#         "drift_depth_hz": 400.0,
#         "drift_period_sec": 4 * 60.0,
#         "amp_lfo_depth": 0.25,
#         "amp_lfo_period_sec": 2.5 * 60.0,
#     },
#     # Slightly darker, slower breathing.
#     "BASE_C": {
#         "center_freq_hz": 2400.0,
#         "drift_depth_hz": 250.0,
#         "drift_period_sec": 6 * 60.0,
#         "amp_lfo_depth": 0.15,
#         "amp_lfo_period_sec": 4 * 60.0,
#     },
#     # Wider drift, a bit more unstable.
#     "BASE_D": {
#         "center_freq_hz": 3000.0,
#         "drift_depth_hz": 600.0,
#         "drift_period_sec": 7 * 60.0,
#         "amp_lfo_depth": 0.3,
#         "amp_lfo_period_sec": 3.5 * 60.0,
#     },
# }

BASE_VARIANTS = {
    # A: Strong, clear movement – fast drift + pronounced breathing
    "BASE_A": {
        # Center the noise in the audible mids (very recognizable).
        "center_freq_hz": 2800.0,

        # How far the filter swings around the center.
        # Larger = brighter → darker → brighter → darker movement.
        "drift_depth_hz": 1200.0,   # exaggerated (was ±300)

        # How long the drift cycle lasts.
        # Smaller = faster motion.
        "drift_period_sec": 45.0,   # 45 seconds (was 5 minutes)

        # Amplitude breathing (percentage change)
        "amp_lfo_depth": 0.45,      # ±45% (was 20%)
        "amp_lfo_period_sec": 30.0, # faster breathing (was 3 minutes)
    },

    # B: Even more unstable with very wide spectral swings
    "BASE_B": {
        "center_freq_hz": 3000.0,
        "drift_depth_hz": 1800.0,   # very wide range for testing motion
        "drift_period_sec": 30.0,   # fast shimmer
        "amp_lfo_depth": 0.55,      # ±55%
        "amp_lfo_period_sec": 25.0,
    },

    # C: Lower band, rumbling-noise character, slower breathing
    "BASE_C": {
        "center_freq_hz": 1800.0,   # darker base layer
        "drift_depth_hz": 900.0,
        "drift_period_sec": 60.0,   # 1-minute drift cycle
        "amp_lfo_depth": 0.35,
        "amp_lfo_period_sec": 45.0,
    },

    # D: Extremely unstable test noise – “breathing monster”
    "BASE_D": {
        "center_freq_hz": 2600.0,
        "drift_depth_hz": 2200.0,   # nearly full spectrum shift
        "drift_period_sec": 20.0,   # rapid dramatic change
        "amp_lfo_depth": 0.65,      # huge amplitude dynamics
        "amp_lfo_period_sec": 20.0,
    },
}


# =========================================================
# BASE EIGENRAUSCH SYNTH VOICE
# =========================================================

# class EigenBase:
#     """
#     One "base" Eigenrausch voice.
#
#     Concept:
#     - Start with pink noise (similar to 1/f noise, soft and ear-friendly).
#     - Run it through a bandpass filter centered around some mid frequency.
#     - Slowly drift the filter center frequency over time (eigengrau shimmer).
#     - Add a very slow amplitude LFO ("breathing" of the noise field).
#     """
#
#     def __init__(
#         self,
#         server: Server,
#         center_freq_hz: float = 2800.0,
#         drift_depth_hz: float = 300.0,
#         drift_period_sec: float = 5 * 60.0,
#         amp_lfo_depth: float = 0.2,
#         amp_lfo_period_sec: float = 3 * 60.0,
#         out_db: float = BASE_OUT_DB,
#     ):
#         self.server = server
#
#         # Base noise source.
#         self.noise = PinkNoise()
#
#         # Frequency drift LFO (very slow).
#         self.freq_lfo = Sine(
#             freq=1.0 / drift_period_sec
#         ).range(
#             center_freq_hz - drift_depth_hz,
#             center_freq_hz + drift_depth_hz,
#         )
#
#         # Band-pass filter with slowly moving center frequency.
#         self.filter = ButBP(
#             self.noise,
#             freq=self.freq_lfo,
#             q=2.0,  # fairly wide band
#         )
#
#         # Amplitude LFO (breathing).
#         self.amp_lfo = Sine(
#             freq=1.0 / amp_lfo_period_sec
#         ).range(
#             1.0 - amp_lfo_depth,
#             1.0 + amp_lfo_depth,
#         )
#
#         # Convert master dBFS level + empirical trim to linear factor.
#         # out_db is the "design" level; BASE_TRIM_DB is the normalization fudge
#         # to push BASE_* renders closer to ~ -1 dBFS.
#         self.base_amp = db_to_amp(out_db + BASE_TRIM_DB)
#
#         # Final signal.
#         self.out_sig = self.filter * self.base_amp * self.amp_lfo
class EigenBase:
    """
    One "base" Eigenrausch voice.

    Concept:
    - Start with pink noise (similar to 1/f noise, soft and ear-friendly).
    - Run it through a bandpass filter centered around some mid frequency.
    - Slowly drift the filter center frequency over time (eigengrau shimmer).
    - Add a very slow amplitude LFO ("breathing" of the noise field).

    Gain structure:
    - Internally, the signal is treated as relative to 0 dBFS.
    - The final stem level is set by a single master gain:
        out_db (from config) + BASE_TRIM_DB (empirical normalization),
      applied at the very end to the whole BASE layer.
    """

    def __init__(
        self,
        server: Server,
        center_freq_hz: float = 2800.0,
        drift_depth_hz: float = 300.0,
        drift_period_sec: float = 5 * 60.0,
        amp_lfo_depth: float = 0.2,
        amp_lfo_period_sec: float = 3 * 60.0,
        out_db: float = BASE_OUT_DB,
    ):
        self.server = server

        # 1) Base noise source, full-scale pink noise (relative to 0 dBFS).
        self.noise = PinkNoise()

        # 2) Frequency drift LFO (very slow).
        self.freq_lfo = Sine(
            freq=1.0 / drift_period_sec
        ).range(
            center_freq_hz - drift_depth_hz,
            center_freq_hz + drift_depth_hz,
        )

        # 3) Band-pass filter with slowly moving center frequency.
        #    Q controls the bandwidth; higher Q = narrower band.
        self.filter = ButBP(
            self.noise,
            freq=self.freq_lfo,
            q=2.0,  # fairly wide band
        )

        # 4) Amplitude LFO (breathing) in linear gain domain.
        #    amp_lfo_depth = ±percentage variation around 1.0.
        self.amp_lfo = Sine(
            freq=1.0 / amp_lfo_period_sec
        ).range(
            1.0 - amp_lfo_depth,
            1.0 + amp_lfo_depth,
        )

        # 5) Pre-mix: filtered pink noise with slow amplitude breathing.
        #    At this stage, everything is still relative to 0 dBFS.
        premix = self.filter * self.amp_lfo

        # 6) Single master gain for the entire BASE stem:
        #    - out_db  = design level from config (BASE_OUT_DB)
        #    - BASE_TRIM_DB = empirical normalization to push BASE_*
        #      towards the desired peak (e.g. ~ -1 dBFS after render).
        layer_amp = db_to_amp(out_db + BASE_TRIM_DB)

        # 7) Final signal.
        self.out_sig = premix * layer_amp

    def out(self):
        """Start sending the signal to the audio output."""
        self.out_sig.out()
        return self

# =========================================================
# PREVIEW & RENDER HELPERS (BASE ONLY)
# =========================================================

def _make_server(device_index: Optional[int]) -> Server:
    """Create and boot a pyo Server for a given device index (BASE)."""
    if device_index is None:
        device_index = pa_get_default_output()

    s = Server(sr=SAMPLE_RATE, nchnls=1, buffersize=1024, duplex=0)
    s.setOutputDevice(device_index)
    s.setVerbosity(0)  # <- suppress most pyo console messages (including Portmidi warning)
    s.boot()
    return s


def preview_base_variant(variant_name: str, device_index: Optional[int] = None) -> None:
    """Realtime preview of a single BASE variant."""
    if variant_name not in BASE_VARIANTS:
        raise ValueError(
            f"Unknown BASE variant '{variant_name}'. "
            f"Available: {', '.join(BASE_VARIANTS.keys())}"
        )

    variant = BASE_VARIANTS[variant_name]

    print(f"[PREVIEW BASE] Starting BASE variant: {variant_name}")
    print("Parameters:")
    for k, v in variant.items():
        print(f"  {k}: {v}")
    print(f"  out_db: {BASE_OUT_DB} dBFS")
    print("Press Enter or Ctrl+C to stop.\n")

    s = _make_server(device_index)

    voice = EigenBase(
        server=s,
        center_freq_hz=variant["center_freq_hz"],
        drift_depth_hz=variant["drift_depth_hz"],
        drift_period_sec=variant["drift_period_sec"],
        amp_lfo_depth=variant["amp_lfo_depth"],
        amp_lfo_period_sec=variant["amp_lfo_period_sec"],
        out_db=BASE_OUT_DB,
    ).out()

    s.start()

    try:
        print("\n[PREVIEW BASE] Eigenrausch BASE is now playing.")
        print("Press Enter to stop (or Ctrl+C)...\n")
        input()
    except KeyboardInterrupt:
        print("\n[PREVIEW BASE] Stopping on Ctrl+C...\n")
    finally:
        s.stop()
        s.shutdown()


def render_base_variant(variant_name: str, device_index: Optional[int] = None) -> None:
    """Render a single BASE variant to WAV."""
    if variant_name not in BASE_VARIANTS:
        raise ValueError(
            f"Unknown BASE variant '{variant_name}'. "
            f"Available: {', '.join(BASE_VARIANTS.keys())}"
        )

    variant = BASE_VARIANTS[variant_name]

    filename = OUTPUT_DIR_BASE / f"{variant_name}.wav"
    print(f"[RENDER BASE] Rendering {variant_name} to: {filename}")
    print(f"  Duration: {DURATION_SEC} seconds")
    print(f"  Sample rate: {SAMPLE_RATE} Hz")

    if device_index is None:
        device_index = pa_get_default_output()
    print(f"  Using output device index: {device_index}\n")

    s = Server(sr=SAMPLE_RATE, nchnls=1, buffersize=1024, duplex=0)
    s.setOutputDevice(device_index)
    s.boot()

    voice = EigenBase(
        server=s,
        center_freq_hz=variant["center_freq_hz"],
        drift_depth_hz=variant["drift_depth_hz"],
        drift_period_sec=variant["drift_period_sec"],
        amp_lfo_depth=variant["amp_lfo_depth"],
        amp_lfo_period_sec=variant["amp_lfo_period_sec"],
        out_db=BASE_OUT_DB,
    ).out()

    s.recordOptions(
        dur=DURATION_SEC,
        filename=str(filename),
        fileformat=0,   # WAV
        sampletype=1,   # 24-bit int
    )

    s.start()
    s.recstart()

    print("[RENDER BASE] Recording started...\n")

    try:
        time.sleep(DURATION_SEC)
    except KeyboardInterrupt:
        print("\n[RENDER BASE] Interrupted by user, stopping early...\n")
    finally:
        s.recstop()
        s.stop()
        s.shutdown()

    print(f"[RENDER BASE] Done: {filename}\n")


def render_all_base_variants(device_index: Optional[int] = None) -> None:
    """Render all BASE_* variants."""
    for name in BASE_VARIANTS.keys():
        render_base_variant(name, device_index=device_index)
