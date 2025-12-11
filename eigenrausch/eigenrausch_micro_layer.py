"""
eigenrausch_micro_layer.py

Eigenrausch MICRO layer (EXAGGERATED TEST VERSION):
- high-frequency micro-tones (tinnitus-like)
- faster random appearance / disappearance
- more tones, more motion, louder by default
"""

import time
from typing import Optional

from pyo import (
    Server,
    PinkNoise,
    Sine,
    Randi,
    pa_get_default_output,
)

from eigenrausch_config import (
    SAMPLE_RATE,
    DURATION_SEC,
    OUTPUT_DIR_MICRO,
    MICRO_OUT_DB,
    db_to_amp,
)


# ---------------------------------------------------------
# MICRO variant definitions
# ---------------------------------------------------------
# Controls per variant:
# - freq_min_hz / freq_max_hz : frequency range of the micro-tones.
# - num_tones                 : how many independent tones/glints.
# - amp_lfo_freq_min/max      : how fast the tone amplitudes change (Hz).
# - noise_db                  : level of underlying noise bed (dBFS).
# - tone_db                   : base level of the sines (dBFS).
#
# GENERAL SONIC EFFECTS:
# - Higher num_tones          → denser swarm, more "halo" / shimmer.
# - Higher amp_lfo_freq_*     → faster flicker, more nervous / animated.
# - Less negative noise_db    → louder hiss bed (more constant presence).
# - Less negative tone_db     → louder tones, more "tinnitus spotlight".
#

# MICRO_VARIANTS = {
#     "MICRO_A": {  # clear, obvious shimmer (good for testing)
#         "freq_min_hz": 6000.0,      # high-mid start
#         "freq_max_hz": 14000.0,     # up into "air" band
#         "num_tones": 8,             # more tones → thicker halo
#         "amp_lfo_freq_min": 0.2,    # amplitudes change roughly 0.2–0.8 Hz
#         "amp_lfo_freq_max": 0.8,    # → ~1–5 changes per second
#         "noise_db": -45.0,          # fairly audible hiss bed
#         "tone_db": -15.0,           # strong sines (very clear for testing)
#     },
#     "MICRO_B": {  # dense, nervous swarm
#         "freq_min_hz": 5000.0,
#         "freq_max_hz": 15000.0,
#         "num_tones": 12,            # thicker cluster
#         "amp_lfo_freq_min": 0.4,
#         "amp_lfo_freq_max": 1.5,    # faster modulation → agitated shimmer
#         "noise_db": -48.0,
#         "tone_db": -18.0,
#     },
#     "MICRO_C": {  # lower shimmer, more "body"
#         "freq_min_hz": 3000.0,      # starts in upper mids
#         "freq_max_hz": 12000.0,
#         "num_tones": 10,
#         "amp_lfo_freq_min": 0.15,
#         "amp_lfo_freq_max": 0.7,
#         "noise_db": -47.0,
#         "tone_db": -16.0,
#     },
#     "MICRO_D": {  # pronounced but sparse, “ghost tones”
#         "freq_min_hz": 8000.0,
#         "freq_max_hz": 16000.0,
#         "num_tones": 5,
#         "amp_lfo_freq_min": 0.05,   # slower motions
#         "amp_lfo_freq_max": 0.3,
#         "noise_db": -50.0,
#         "tone_db": -18.0,
#     },
# }
# MICRO_VARIANTS = {
#     "MICRO_A": {  # clearly audible shimmer in upper mids
#         # 2–6 kHz → safely inside your hearing, still "micro" and not melodic.
#         "freq_min_hz": 2000.0,
#         "freq_max_hz": 6000.0,
#         "num_tones": 8,
#         "amp_lfo_freq_min": 0.2,
#         "amp_lfo_freq_max": 0.8,
#         "noise_db": -45.0,
#         "tone_db": -15.0,
#     },
#     "MICRO_B": {  # brighter, pushes up towards your upper limit
#         # 3–8 kHz → gets close to the top of your 6–10k band.
#         "freq_min_hz": 3000.0,
#         "freq_max_hz": 8000.0,
#         "num_tones": 12,
#         "amp_lfo_freq_min": 0.4,
#         "amp_lfo_freq_max": 1.5,
#         "noise_db": -48.0,
#         "tone_db": -18.0,
#     },
#     "MICRO_C": {  # mostly in your "sweet zone"
#         # 4–9 kHz → right through 6–9k, so should be very noticeable.
#         "freq_min_hz": 4000.0,
#         "freq_max_hz": 9000.0,
#         "num_tones": 10,
#         "amp_lfo_freq_min": 0.15,
#         "amp_lfo_freq_max": 0.7,
#         "noise_db": -47.0,
#         "tone_db": -16.0,
#     },
#     "MICRO_D": {  # sparser, near the top edge of your hearing
#         # 5–10 kHz → hugs your 6–10k band closer to the top.
#         "freq_min_hz": 5000.0,
#         "freq_max_hz": 10000.0,
#         "num_tones": 5,
#         "amp_lfo_freq_min": 0.05,
#         "amp_lfo_freq_max": 0.3,
#         "noise_db": -50.0,
#         "tone_db": -18.0,
#     },
# }

MICRO_VARIANTS = {
    "MICRO_A": {  # ~18–25 yrs: very young ears, lots of ultra-high content
        # Mostly above where 50+ will hear clearly.
        "freq_min_hz": 10000.0,    # 10 kHz
        "freq_max_hz": 18000.0,    # up into “almost ultrasonic”
        "num_tones": 8,
        "amp_lfo_freq_min": 0.2,
        "amp_lfo_freq_max": 0.8,
        "noise_db": -45.0,
        "tone_db": -15.0,
    },
    "MICRO_B": {  # ~30–40 yrs: still bright, but slightly less extreme highs
        # Band slides down a bit: still a lot above 10 kHz, some in the 8–12 k range.
        "freq_min_hz": 8000.0,     # 8 kHz
        "freq_max_hz": 16000.0,
        "num_tones": 12,
        "amp_lfo_freq_min": 0.4,
        "amp_lfo_freq_max": 1.5,
        "noise_db": -48.0,
        "tone_db": -18.0,
    },
    "MICRO_C": {  # ~40–50 yrs: centred more in the classic “sensitivity plateau”
        # 6–14 kHz: still airy, but more in the range many mid-age ears can perceive.
        "freq_min_hz": 6000.0,     # 6 kHz
        "freq_max_hz": 14000.0,
        "num_tones": 10,
        "amp_lfo_freq_min": 0.15,
        "amp_lfo_freq_max": 0.7,
        "noise_db": -47.0,
        "tone_db": -16.0,
    },
    "MICRO_D": {  # 50+ yrs: shifted further down into 4–10 kHz
        # Designed to sit where you said your own ears live (~6–10 kHz),
        # with some extra content below for warmth / audibility.
        "freq_min_hz": 4000.0,     # 4 kHz (upper mids)
        "freq_max_hz": 10000.0,    # 10 kHz (top of your band)
        "num_tones": 5,
        "amp_lfo_freq_min": 0.05,
        "amp_lfo_freq_max": 0.3,
        "noise_db": -50.0,
        "tone_db": -18.0,
    },
}

# =========================================================
# MICRO-TONE EIGENRAUSCH VOICE
# =========================================================

class EigenMicro:
    """
    EXAGGERATED Micro-tone layer for Eigenrausch.

    Concept:
    - High-frequency sine swarm over a light noise bed.
    - Each sine:
      - wanders in frequency within [freq_min_hz, freq_max_hz]
      - has a random amplitude LFO making it fade in/out
    - Additional shaping on amplitude to make "hot spots" more pronounced
      (small amplitudes pushed down, loud ones stay loud).
    """

    def __init__(
        self,
        server: Server,
        freq_min_hz: float = 7000.0,
        freq_max_hz: float = 12000.0,
        num_tones: int = 4,
        amp_lfo_freq_min: float = 0.01,
        amp_lfo_freq_max: float = 0.05,
        noise_db: float = -50.0,
        tone_db: float = -30.0,
        out_db: float = MICRO_OUT_DB,
    ):
        self.server = server

        # 1) High-frequency noise bed (very soft, mostly for "air").
        #    Less negative noise_db → louder bed, more hiss.
        self.noise = PinkNoise() * db_to_amp(noise_db)

        # Keep references so pyo doesn't garbage-collect them.
        self.freq_lfos = []
        self.freq_rate_lfos = []
        self.amp_rate_lfos = []
        self.amp_lfos = []
        self.tones = []

        # Base loudness:
        # tone_db = how loud each sine can be at max,
        # out_db  = overall trim for the whole MICRO layer (from config).
        tone_base_amp = db_to_amp(tone_db)
        layer_amp = db_to_amp(out_db)

        for _ in range(num_tones):
            # 2) Frequency rate LFO:
            #    Randomly changes how fast the frequency wanders.
            #    → Makes motion feel less mechanical, more organic.
            freq_rate_lfo = Randi(
                min=0.01,   # min wander speed (very slow)
                max=0.1,    # max wander speed (a few changes per second)
                freq=0.05,  # how often this *rate* morphs
            )

            # 3) Frequency LFO:
            #    Sine's pitch drifts between freq_min_hz and freq_max_hz.
            freq_lfo = Randi(
                min=freq_min_hz,
                max=freq_max_hz,
                freq=freq_rate_lfo,
            )

            # 4) Amplitude rate LFO:
            #    Controls how quickly the amplitude LFO moves (in Hz range).
            amp_freq = Randi(
                min=amp_lfo_freq_min,
                max=amp_lfo_freq_max,
                freq=0.1,  # how often the *rate* itself is randomized
            )

            # 5) Amplitude LFO:
            #    Random value between 0 and 1, changing at amp_freq.
            #    This gives each tone independent fade-in / fade-out behaviour.
            amp_lfo = Randi(
                min=0.0,
                max=1.0,
                freq=amp_freq,
            )

            # 6) SHAPE the amplitude:
            #    We square it to emphasize bright moments:
            #       small values (0–0.5) become much quieter,
            #       values near 1.0 stay strong.
            #    → micro-tones appear as more distinct "hot spots" instead of
            #      a constant wash.
            shaped_amp = amp_lfo ** 2

            # 7) High-frequency sine "glint" itself.
            tone = Sine(freq=freq_lfo, mul=shaped_amp * tone_base_amp * layer_amp)

            self.freq_rate_lfos.append(freq_rate_lfo)
            self.freq_lfos.append(freq_lfo)
            self.amp_rate_lfos.append(amp_freq)
            self.amp_lfos.append(amp_lfo)
            self.tones.append(tone)

        tones_sum = sum(self.tones)

        # 8) Final signal: noise bed + clustered tones.
        self.out_sig = self.noise + tones_sum

    def out(self):
        """Start sending the signal to the audio output."""
        self.out_sig.out()
        return self


# =========================================================
# PREVIEW & RENDER HELPERS (MICRO ONLY)
# =========================================================

def _make_server(device_index: Optional[int]) -> Server:
    """Create and boot a pyo Server for a given device index (MICRO)."""
    if device_index is None:
        device_index = pa_get_default_output()

    s = Server(sr=SAMPLE_RATE, nchnls=1, buffersize=1024, duplex=0)
    s.setOutputDevice(device_index)
    s.setVerbosity(0)  # <- suppress most pyo console messages (including Portmidi warning)
    s.boot()
    return s


def preview_micro_variant(variant_name: str, device_index: Optional[int] = None) -> None:
    """Realtime preview of a single MICRO variant."""
    if variant_name not in MICRO_VARIANTS:
        raise ValueError(
            f"Unknown MICRO variant '{variant_name}'. "
            f"Available: {', '.join(MICRO_VARIANTS.keys())}"
        )

    variant = MICRO_VARIANTS[variant_name]

    print(f"[PREVIEW MICRO] Starting MICRO variant: {variant_name}")
    print("Parameters:")
    for k, v in variant.items():
        print(f"  {k}: {v}")
    print(f"  out_db (layer): {MICRO_OUT_DB} dBFS")
    print("Press Enter or Ctrl+C to stop.\n")

    s = _make_server(device_index)

    voice = EigenMicro(
        server=s,
        freq_min_hz=variant["freq_min_hz"],
        freq_max_hz=variant["freq_max_hz"],
        num_tones=variant["num_tones"],
        amp_lfo_freq_min=variant["amp_lfo_freq_min"],
        amp_lfo_freq_max=variant["amp_lfo_freq_max"],
        noise_db=variant["noise_db"],
        tone_db=variant["tone_db"],
        out_db=MICRO_OUT_DB,
    ).out()

    s.start()

    try:
        print("\n[PREVIEW MICRO] Eigenrausch MICRO is now playing.")
        print("Press Enter to stop (or Ctrl+C)...\n")
        input()
    except KeyboardInterrupt:
        print("\n[PREVIEW MICRO] Stopping on Ctrl+C...\n")
    finally:
        s.stop()
        s.shutdown()


def render_micro_variant(variant_name: str, device_index: Optional[int] = None) -> None:
    """Render a single MICRO variant to WAV."""
    if variant_name not in MICRO_VARIANTS:
        raise ValueError(
            f"Unknown MICRO variant '{variant_name}'. "
            f"Available: {', '.join(MICRO_VARIANTS.keys())}"
        )

    variant = MICRO_VARIANTS[variant_name]

    filename = OUTPUT_DIR_MICRO / f"{variant_name}.wav"
    print(f"[RENDER MICRO] Rendering {variant_name} to: {filename}")
    print(f"  Duration: {DURATION_SEC} seconds")
    print(f"  Sample rate: {SAMPLE_RATE} Hz")

    if device_index is None:
        device_index = pa_get_default_output()
    print(f"  Using output device index: {device_index}\n")

    s = Server(sr=SAMPLE_RATE, nchnls=1, buffersize=1024, duplex=0)
    s.setOutputDevice(device_index)
    s.boot()

    voice = EigenMicro(
        server=s,
        freq_min_hz=variant["freq_min_hz"],
        freq_max_hz=variant["freq_max_hz"],
        num_tones=variant["num_tones"],
        amp_lfo_freq_min=variant["amp_lfo_freq_min"],
        amp_lfo_freq_max=variant["amp_lfo_freq_max"],
        noise_db=variant["noise_db"],
        tone_db=variant["tone_db"],
        out_db=MICRO_OUT_DB,
    ).out()

    s.recordOptions(
        dur=DURATION_SEC,
        filename=str(filename),
        fileformat=0,   # WAV
        sampletype=1,   # 24-bit int
    )

    s.start()
    s.recstart()

    print("[RENDER MICRO] Recording started...\n")

    try:
        time.sleep(DURATION_SEC)
    except KeyboardInterrupt:
        print("\n[RENDER MICRO] Interrupted by user, stopping early...\n")
    finally:
        s.recstop()
        s.stop()
        s.shutdown()

    print(f"[RENDER MICRO] Done: {filename}\n")


def render_all_micro_variants(device_index: Optional[int] = None) -> None:
    """Render all MICRO_* variants."""
    for name in MICRO_VARIANTS.keys():
        render_micro_variant(name, device_index=device_index)
