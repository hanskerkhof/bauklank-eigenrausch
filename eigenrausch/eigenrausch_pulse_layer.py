"""
eigenrausch_pulse_layer.py

Eigenrausch PULSE layer:
- irregular, short noise bursts (clicky/pulse-like energy)
- sits inside a very quiet noise bed
"""

import time
from typing import Optional

from pyo import (
    Server,
    PinkNoise,
    ButBP,
    Randi,
    pa_get_default_output,
)

from eigenrausch_config import (
    SAMPLE_RATE,
    DURATION_SEC,
    OUTPUT_DIR_PULSE,
    PULSE_OUT_DB,
    PULSE_TRIM_DB,
    db_to_amp,
)


# ---------------------------------------------------------
# PULSE variant definitions
# ---------------------------------------------------------
# Controls (per variant):
# - freq_min_hz / freq_max_hz : spectral band for the pulses
# - pulse_rate_min/max        : how fast pulses happen (in Hz, i.e. events per second)
# - noise_db                  : level of underlying noise bed (dBFS)
# - pulse_db                  : nominal level of the pulse component (dBFS)
#
# NOTE:
# Higher pulse_rate_*  = more frequent pulses
# Higher pulse_db      = louder pulses
# Lower noise_db       = quieter bed → more contrast, pulses “pop” more

PULSE_VARIANTS = {
#     "PULSE_A": {  # clear, medium-fast pulses (default "show me the effect")
#         "freq_min_hz": 1500.0,   # lower bound of pulse spectrum
#         "freq_max_hz": 4500.0,   # upper bound (mid + presence band)
#         "pulse_rate_min": 1.5,   # min 1.5 pulses per second
#         "pulse_rate_max": 4.0,   # up to 4 pulses per second
#         "noise_db": -60.0,       # very quiet bed → strong contrast
#         "pulse_db": -10.0,       # fairly loud pulses
#     },
#     "PULSE_B": {  # brighter, denser pulses
#         "freq_min_hz": 2500.0,
#         "freq_max_hz": 6000.0,
#         "pulse_rate_min": 2.0,   # faster flicker
#         "pulse_rate_max": 6.0,
#         "noise_db": -58.0,
#         "pulse_db": -8.0,
#     },
#     "PULSE_C": {  # darker, chunkier, less bright
#         "freq_min_hz": 800.0,
#         "freq_max_hz": 3000.0,
#         "pulse_rate_min": 1.0,
#         "pulse_rate_max": 3.0,
#         "noise_db": -55.0,
#         "pulse_db": -9.0,
#     },
#     "PULSE_D": {  # sparse, almost distant thumps
#         "freq_min_hz": 1200.0,
#         "freq_max_hz": 4000.0,
#         "pulse_rate_min": 0.5,   # slower, more occasional
#         "pulse_rate_max": 1.5,
#         "noise_db": -62.0,
#         "pulse_db": -12.0,
#     },
    "PULSE_A": {  # clear, medium-fast pulses (default "show me the effect")
        "freq_min_hz": 1500.0,
        "freq_max_hz": 4500.0,
        "pulse_rate_min": 1.5,
        "pulse_rate_max": 4.0,
        "noise_db": -60.0,
        "pulse_db": -10.0,
    },
    "PULSE_B": {  # brighter, denser pulses
        "freq_min_hz": 2500.0,
        "freq_max_hz": 6000.0,
        "pulse_rate_min": 2.0,
        "pulse_rate_max": 6.0,
        "noise_db": -58.0,
        "pulse_db": -8.0,
    },
    "PULSE_C": {  # darker, chunkier, less bright
        "freq_min_hz": 800.0,
        "freq_max_hz": 3000.0,
        "pulse_rate_min": 1.0,
        "pulse_rate_max": 3.0,
        "noise_db": -55.0,
        "pulse_db": -9.0,
    },
    "PULSE_D": {  # sparse, almost distant thumps
        "freq_min_hz": 1200.0,
        "freq_max_hz": 4000.0,
        "pulse_rate_min": 0.5,
        "pulse_rate_max": 1.5,
        "noise_db": -62.0,
        "pulse_db": -12.0,
    },
    "PULSE_CRACKLE": {  # static crackle: small HF pops like dust on vinyl
        # Crackle = more high-frequency content
        "freq_min_hz": 6000.0,   # keep band mostly in the high region
        "freq_max_hz": 14000.0,

        # Crackle should be *many tiny* pops, not big whoomps:
        # Higher rate = lots of small events, feels like continuous static.
        "pulse_rate_min": 8.0,   # 8–20 pulses per second
        "pulse_rate_max": 20.0,

        # Very quiet bed – you almost don’t want to perceive a “bed”, just the crackle.
        "noise_db": -70.0,

        # Individual crackles should *poke through* but not destroy ears.
        "pulse_db": -18.0,
    },
}


# =========================================================
# PULSE EIGENRAUSCH VOICE
# =========================================================

# class EigenPulse:
#     """
#     Exaggerated Pulse layer for Eigenrausch.
#
#     Now produces:
#     - clearly audible, frequent bursts
#     - more contrast between pulses and noise bed
#     - wider-band clicks (less tonal, more transient)
#     """
#
#     def __init__(
#         self,
#         server: Server,
#         freq_min_hz: float = 1500.0,
#         freq_max_hz: float = 4500.0,
#         # These defaults are overridden by PULSE_VARIANTS, but they document the "typical" region.
#         pulse_rate_min: float = 1.5,    # was 0.05…0.2 — now MUCH faster
#         pulse_rate_max: float = 4.0,    # 1.5–4 pulses per second (random)
#         noise_db: float = -60.0,        # make bed quieter → pulses stand out more
#         pulse_db: float = -10.0,        # was around -20 dB — raise pulse volume
#         out_db: float = PULSE_OUT_DB,
#     ):
#         self.server = server
#
#         # 1) Very quiet base noise bed
#         #    Lower (more negative) noise_db → quieter bed → more contrast.
#         self.noise_bed = PinkNoise() * db_to_amp(noise_db)
#
#         # 2) Pulse noise source (raw, full-band pink noise).
#         self.pulse_noise = PinkNoise()
#
#         # 3) Frequency drift of the resonant filter — slowish color change over time.
#         #    Higher freq -> more movement in timbre; lower -> more static.
#         self.freq_lfo = Randi(
#             min=freq_min_hz,
#             max=freq_max_hz,
#             freq=0.05,   # Hz – how fast the center frequency slides between min/max
#         )
#
#         # 4) Wider band-pass = less tonal, more “burst-like” noise.
#         #    Lower Q → wider band, more "noisy"; higher Q → narrower, more "pitched".
#         self.band = ButBP(
#             self.pulse_noise,
#             freq=self.freq_lfo,
#             q=1.2,      # was q=5 — narrow → tonal. Lower Q → noisy, punchy.
#         )
#
#         # 5) Pulse-rate control:
#         #    Random frequency between pulse_rate_min and pulse_rate_max (in Hz).
#         #    This is how OFTEN the amplitude jumps (i.e. how many pulses per second).
#         self.pulse_rate = Randi(
#             min=pulse_rate_min,
#             max=pulse_rate_max,
#             freq=0.5,    # how fast the *rate* itself morphs over time
#         )
#
#         # 6) Amplitude LFO — random steps between 0 and 1, at pulse_rate frequency.
#         #    Each step effectively becomes one "pulse".
#         self.amp_lfo = Randi(
#             min=0.0,
#             max=1.0,
#             freq=self.pulse_rate,
#         )
#
#         # 7) SHAPE the amplitude spikes to make them more “spiky”:
#         #    amp^3 exaggerates the top of each pulse:
#         #      - small values (0–0.5) become even smaller
#         #      - high values (0.8–1.0) stay relatively high
#         #    → fewer medium loud pulses, more clearly separated "hits".
#         shaped_amp = self.amp_lfo ** 3
#
#         # 8) Convert pulse + layer volume to linear multipliers.
#         #    pulse_db   controls loudness of the pulse content itself.
#         #    out_db     is the overall trim for the whole PULSE layer (from config).
#         pulse_amp = db_to_amp(pulse_db)
#
#         # Master layer gain (pulse) = out_db + empirical trim.
#         layer_amp = db_to_amp(out_db + PULSE_TRIM_DB)
#
#         # 9) Pulse signal = bandpassed noise * shaped amplitude envelope * gains.
#         self.pulse_sig = self.band * shaped_amp * pulse_amp * layer_amp
#
#         # 10) Final mix = quiet bed + pulse bursts.
#         self.out_sig = self.noise_bed + self.pulse_sig
class EigenPulse:
    """
    Exaggerated Pulse layer for Eigenrausch.

    Concept:
    - Very quiet noise bed (relative level set by noise_db).
    - Band-limited noise bursts ("pulses") whose level is set by pulse_db.
    - All internal levels are defined relative to 0 dBFS.
    - A single master gain (out_db + PULSE_TRIM_DB) is applied at the end
      to normalize the whole PULSE stem.
    """

    def __init__(
        self,
        server: Server,
        freq_min_hz: float = 1500.0,
        freq_max_hz: float = 4500.0,
        # These defaults are overridden by PULSE_VARIANTS, but they document the "typical" region.
        pulse_rate_min: float = 1.5,    # pulses per second (min)
        pulse_rate_max: float = 4.0,    # pulses per second (max)
        noise_db: float = -60.0,        # bed level, relative to 0 dBFS
        pulse_db: float = -10.0,        # pulse level, relative to 0 dBFS
        out_db: float = PULSE_OUT_DB,
    ):
        self.server = server

        # 1) Very quiet base noise bed (relative to 0 dBFS).
        #    Lower (more negative) noise_db → quieter bed → more contrast.
        self.noise_bed = PinkNoise() * db_to_amp(noise_db)

        # 2) Pulse noise source (raw, full-band pink noise).
        self.pulse_noise = PinkNoise()

        # 3) Frequency drift of the resonant filter — slowish color change over time.
        self.freq_lfo = Randi(
            min=freq_min_hz,
            max=freq_max_hz,
            freq=0.05,   # Hz – how fast the center frequency slides between min/max
        )

        # 4) Band-pass filter.
        #    Lower Q → wider band, more "noisy"; higher Q → narrower, more "pitched".
        self.band = ButBP(
            self.pulse_noise,
            freq=self.freq_lfo,
            q=1.2,      # fairly wide for noisy, burst-like character
        )

        # 5) Pulse-rate control:
        #    Random frequency between pulse_rate_min and pulse_rate_max (in Hz).
        #    This is how OFTEN the amplitude jumps (pulses per second).
        self.pulse_rate = Randi(
            min=pulse_rate_min,
            max=pulse_rate_max,
            freq=0.5,    # how fast the *rate* itself morphs over time
        )

        # 6) Amplitude LFO — random steps between 0 and 1, at pulse_rate frequency.
        self.amp_lfo = Randi(
            min=0.0,
            max=1.0,
            freq=self.pulse_rate,
        )

        # 7) Shape the amplitude spikes to make them more “spiky”.
        #    amp^3 exaggerates peaks and suppresses medium/low values.
        shaped_amp = self.amp_lfo ** 3

        # 8) Pulse amplitude relative to 0 dBFS.
        pulse_amp = db_to_amp(pulse_db)

        # 9) Pulse signal (still relative to 0 dBFS at this point).
        pulse_sig = self.band * shaped_amp * pulse_amp

        # 10) Pre-mix: noise bed + pulses, both expressed relative to 0 dBFS.
        premix = self.noise_bed + pulse_sig

        # 11) Single master gain for the entire PULSE stem:
        #     out_db is the config level, PULSE_TRIM_DB is empirical normalization.
        layer_amp = db_to_amp(out_db + PULSE_TRIM_DB)

        # 12) Final signal.
        self.out_sig = premix * layer_amp

    def out(self):
        """Start sending the signal to the audio output."""
        self.out_sig.out()
        return self


# =========================================================
# PREVIEW & RENDER HELPERS (PULSE ONLY)
# =========================================================

def _make_server(device_index: Optional[int]) -> Server:
    """Create and boot a pyo Server for a given device index (PULSE)."""
    if device_index is None:
        device_index = pa_get_default_output()

    s = Server(sr=SAMPLE_RATE, nchnls=1, buffersize=1024, duplex=0)
    s.setOutputDevice(device_index)
    s.setVerbosity(0)  # <- suppress most pyo console messages (including Portmidi warning)
    s.boot()
    return s


def preview_pulse_variant(variant_name: str, device_index: Optional[int] = None) -> None:
    """Realtime preview of a single PULSE variant."""
    if variant_name not in PULSE_VARIANTS:
        raise ValueError(
            f"Unknown PULSE variant '{variant_name}'. "
            f"Available: {', '.join(PULSE_VARIANTS.keys())}"
        )

    variant = PULSE_VARIANTS[variant_name]

    print(f"[PREVIEW PULSE] Starting PULSE variant: {variant_name}")
    print("Parameters:")
    for k, v in variant.items():
        print(f"  {k}: {v}")
    print(f"  out_db (layer): {PULSE_OUT_DB} dBFS")
    print("Press Enter or Ctrl+C to stop.\n")

    s = _make_server(device_index)

    voice = EigenPulse(
        server=s,
        freq_min_hz=variant["freq_min_hz"],
        freq_max_hz=variant["freq_max_hz"],
        pulse_rate_min=variant["pulse_rate_min"],
        pulse_rate_max=variant["pulse_rate_max"],
        noise_db=variant["noise_db"],
        pulse_db=variant["pulse_db"],
        out_db=PULSE_OUT_DB,
    ).out()

    s.start()

    try:
        print("\n[PREVIEW PULSE] Eigenrausch PULSE is now playing.")
        print("Press Enter to stop (or Ctrl+C)...\n")
        input()
    except KeyboardInterrupt:
        print("\n[PREVIEW PULSE] Stopping on Ctrl+C...\n")
    finally:
        s.stop()
        s.shutdown()


def render_pulse_variant(variant_name: str, device_index: Optional[int] = None) -> None:
    """Render a single PULSE variant to WAV."""
    if variant_name not in PULSE_VARIANTS:
        raise ValueError(
            f"Unknown PULSE variant '{variant_name}'. "
            f"Available: {', '.join(PULSE_VARIANTS.keys())}"
        )

    variant = PULSE_VARIANTS[variant_name]

    filename = OUTPUT_DIR_PULSE / f"{variant_name}.wav"
    print(f"[RENDER PULSE] Rendering {variant_name} to: {filename}")
    print(f"  Duration: {DURATION_SEC} seconds")
    print(f"  Sample rate: {SAMPLE_RATE} Hz")

    if device_index is None:
        device_index = pa_get_default_output()
    print(f"  Using output device index: {device_index}\n")

    s = Server(sr=SAMPLE_RATE, nchnls=1, buffersize=1024, duplex=0)
    s.setOutputDevice(device_index)
    s.boot()

    voice = EigenPulse(
        server=s,
        freq_min_hz=variant["freq_min_hz"],
        freq_max_hz=variant["freq_max_hz"],
        pulse_rate_min=variant["pulse_rate_min"],
        pulse_rate_max=variant["pulse_rate_max"],
        noise_db=variant["noise_db"],
        pulse_db=variant["pulse_db"],
        out_db=PULSE_OUT_DB,
    ).out()

    s.recordOptions(
        dur=DURATION_SEC,
        filename=str(filename),
        fileformat=0,   # WAV
        sampletype=1,   # 24-bit int
    )

    s.start()
    s.recstart()

    print("[RENDER PULSE] Recording started...\n")

    try:
        time.sleep(DURATION_SEC)
    except KeyboardInterrupt:
        print("\n[RENDER PULSE] Interrupted by user, stopping early...\n")
    finally:
        s.recstop()
        s.stop()
        s.shutdown()

    print(f"[RENDER PULSE] Done: {filename}\n")


def render_all_pulse_variants(device_index: Optional[int] = None) -> None:
    """Render all PULSE_* variants."""
    for name in PULSE_VARIANTS.keys():
        render_pulse_variant(name, device_index=device_index)
