# Eigenrausch – Sound Generation Toolkit (pyo)

This toolkit generates the three layers of the **Eigenrausch** sound sculpture:

- **BASE** – drifting band-limited noise (eigengrau translated into sound)  
- **MICRO** – high-frequency micro-tones (age-coded perceptual shimmer)  
- **PULSE** – irregular noise bursts / crackle  

Each layer contains multiple **variants** (A, B, C, D, …), and each variant can be **previewed**, **rendered**, or **batch-exported**.

The system is built on **pyo** (Python DSP engine), and all renders are done **in realtime**.


---

## 📦 Installation

Requires **Python 3.11** (recommended for macOS ARM) and pyo 1.0.5.

### 1. Create and activate a virtualenv

    python3.11 -m venv .venv
    source .venv/bin/activate

### 2. Install Homebrew audio libs (macOS)

    brew install portaudio libsndfile portmidi liblo

### 3. Install pyo

    pip install pyo


## 🧱 Project Structure

    eigenrausch/
    │
    ├── eigenrausch_pyo_main.py        # main CLI dispatcher
    ├── eigenrausch_base_layer.py      # BASE layer engine + variants
    ├── eigenrausch_micro_layer.py     # MICRO layer engine + variants
    ├── eigenrausch_pulse_layer.py     # PULSE layer engine + variants
    ├── eigenrausch_config.py          # global config (duration, sample rate, levels, dirs)
    │
    ├── eigenrausch_bases/             # rendered BASE_*.wav
    ├── eigenrausch_micro/             # rendered MICRO_*.wav
    └── eigenrausch_pulse/             # rendered PULSE_*.wav

## 🎛 Command Overview

    python eigenrausch_pyo_main.py <mode> [options]

Where ````<mode>```` is one of:

- preview – preview one variant in realtime 
- render – render one variant to WAV 
- render_all – render all variants (BASE + MICRO + PULSE)
- list – list all available variants

#### General syntax

    python eigenrausch_pyo_main.py {preview,render,render_all,list} [-h] [-v VARIANT] [--device-index DEVICE_INDEX]

#### Options:

- -v, --variant VARIANT – name of variant (e.g. BASE_A, MICRO_D, PULSE_CRACKLE)
- --device-index N – PortAudio output device index (if omitted: use system default)
- -h, --help – show help

### 🔎 List Available Variants

Show all variants grouped by layer:

    python eigenrausch_pyo_main.py list

Example output:

    Available Eigenrausch variants:
    
      BASE variants:
        - BASE_A
        - BASE_B
        - BASE_C
        - BASE_D
    
      MICRO variants:
        - MICRO_A
        - MICRO_B
        - MICRO_C
        - MICRO_D
    
      PULSE variants:
        - PULSE_A
        - PULSE_B
        - PULSE_C
        - PULSE_D
        - PULSE_CRACKLE

If you add new variants to BASE_VARIANTS, MICRO_VARIANTS, or PULSE_VARIANTS in their respective files, they will automatically appear in list and be accepted by preview and render.

## 🎧 Preview a Variant (Realtime)

Preview any variant (BASE, MICRO, or PULSE) with:

    python eigenrausch_pyo_main.py preview -v <VARIANT_NAME> [--device-index N]

Examples:

Preview BASE

    python eigenrausch_pyo_main.py preview -v BASE_A

Preview MICRO

    python eigenrausch_pyo_main.py preview -v MICRO_D --device-index 4

Preview PULSE

    python eigenrausch_pyo_main.py preview -v PULSE_CRACKLE

- Audio is streamed via pyo’s Server.
- Press Enter (or Ctrl+C) in the terminal to stop.

## 💾 Render a Single Variant

Rendering writes a WAV file to disk in realtime
(2 minutes of sound = ~2 minutes wall clock).

    python eigenrausch_pyo_main.py render -v <VARIANT_NAME> [--device-index N]

Examples:

    # Render a BASE variant
    python eigenrausch_pyo_main.py render -v BASE_C
    
    # Render a MICRO variant, using a specific output device
    python eigenrausch_pyo_main.py render -v MICRO_B --device-index 4
    
    # Render a PULSE variant
    python eigenrausch_pyo_main.py render -v PULSE_A


Output directories (configurable in ````eigenrausch_config.py````):

- BASE → eigenrausch_bases/BASE_*.wav
- MICRO → eigenrausch_micro/MICRO_*.wav
- PULSE → eigenrausch_pulse/PULSE_*.wav

## 📀 Render ALL Variants

Render the entire Eigenrausch palette:

    python eigenrausch_pyo_main.py render_all


This will:

- Render all BASE_* into eigenrausch_bases/
- Render all MICRO_* into eigenrausch_micro/
- Render all PULSE_* into eigenrausch_pulse/

You can also specify a device index:

    python eigenrausch_pyo_main.py render_all --device-index 4


## 🎚 Device Selection (PortAudio)

To inspect available audio output devices, you can use a small pyo test script (e.g. ````pyo_device_test.py````) that calls pa_list_devices() and plays a test tone.

Typical output:

    AUDIO devices:
    0: OUT, name: C34J79x, host api index: 0, default sr: 48000 Hz, latency: 0.009833 s
    1: OUT, name: USB Audio CODEC , host api index: 0, default sr: 48000 Hz, latency: 0.004354 s
    4: OUT, name: MacBook Pro Speakers, host api index: 0, default sr: 44100 Hz, latency: 0.019093 s
    ...

Default output device index: 4

Use the index value with --device-index:

    python eigenrausch_pyo_main.py preview -v BASE_A --device-index 4


## ⚙ Configuration (eigenrausch_config.py)

Global settings for all layers:

- SAMPLE_RATE – e.g. 48000
- DURATION_MIN – render duration in minutes (used by all layers)
- OUTPUT_DIR_BASE, OUTPUT_DIR_MICRO, OUTPUT_DIR_PULSE – output paths
- BASE_OUT_DB, MICRO_OUT_DB, PULSE_OUT_DB – global output levels (dBFS)

Example:

    SAMPLE_RATE = 48000
    DURATION_MIN = 2.0          # 2 minutes per render (for final stems)
    DURATION_SEC = DURATION_MIN * 60
    
    OUTPUT_DIR_BASE = Path("eigenrausch_bases")
    OUTPUT_DIR_MICRO = Path("eigenrausch_micro")
    OUTPUT_DIR_PULSE = Path("eigenrausch_pulse")
    
    BASE_OUT_DB = -10.0
    MICRO_OUT_DB = -5.0
    PULSE_OUT_DB = -2.0

    def db_to_amp(db: float) -> float:
        return 10 ** (db / 20.0)

During design:

- Use a small DURATION_MIN (e.g. 0.05 = 3 seconds) for quick tests.
- Then bump up to longer durations (e.g. 2–10 minutes) for final stems.

## 🧬 Layers Overview

#### BASE Layer (````eigenrausch_base_layer.py````)

- Noise source: pink noise
- Filter: band-pass (````ButBP````) with:
  - drifting center frequency (````freq_lfo````)
  - possibly modulated Q (````q_lfo````)
- Amplitude: slow “breathing” LFO (````amp_lfo````)
- Variants (````BASE_A … BASE_D````) differ in:
  - center frequency (````center_freq_hz````)
  - drift depth / period
  - amplitude depth / period

Exaggerated test settings make movement and breathing clearly audible.
For installation, these can be toned down (longer periods, smaller depths, lower levels).

#### MICRO Layer (````eigenrausch_micro_layer.py````)

- Noise bed: quiet pink noise “air”
- Tones: multiple high-frequency sines:
  - frequency drift within ````[freq_min_hz, freq_max_hz]````
  - random amplitude LFOs with rate ranges
  - non-linear amplitude shaping (````amp_lfo ** 2````) → “hot spots” pop out
- Age-coded variants (````MICRO_A … MICRO_D````):
  - MICRO_A → highest band (young ears, ~18–25)
  - MICRO_B → slightly lower (~30–40)
  - MICRO_C → mid-high band (~40–50)
  - MICRO_D → 4–10 kHz (50+ range)

Conceptually:

- MICRO encodes psychoacoustic aging: as the band shifts down, more people can hear it. 
- In practice, older listeners may only clearly perceive MICRO_C and MICRO_D.

#### PULSE Layer (````eigenrausch_pulse_layer.py````)

- Noise bed: very quiet pink noise
- Pulse source: pink noise → band-pass filter (narrower Q for more “clicky” noise)
- Amplitude: random-step LFO (````Randi````) with:
  - pulse_rate_min/max controlling pulses per second
  - non-linear amplitude shaping (````amp_lfo ** 3````) → spiky bursts
- Variants (````PULSE_A … PULSE_D, PULSE_CRACKLE````):
  - differ in band (low/mid/high), rate, and loudness
  - ````PULSE_CRACKLE```` tuned as high-frequency “static crackle” / dust-on-vinyl style

Conceptually:

- PULSE represents entropy, “events” in the noise floor: glitches, crackles, intrusions that puncture the otherwise smooth eigen-noise.

## 🧠 Concept Summary

- BASE = physiological noise floor
  - what you “hear when you hear nothing”
  - eigengrau translated into band-limited, drifting noise
- MICRO = perceptual aging / attention
  - high-frequency micro-tones that may or may not be audible depending on age
  - variants map roughly to hearing bands across the lifespan
- PULSE = entropy / intrusion
  - irregular events: crackles, bursts, glitches
  - disturbances on top of the otherwise continuous “Eigenrausch” 

Together they form a three-layer sound field that can be:
- spatialised across multiple speakers (e.g. 16 channels)
- tailored per listener age / position
- rendered as stems and played back on independent SD-card players.

## 📝 Example Workflows

#### Quick design test

    # Hear exaggerated BASE motion
    python eigenrausch_pyo_main.py preview -v BASE_A --device-index 4
    
    # Hear age-coded MICRO for 50+
    python eigenrausch_pyo_main.py preview -v MICRO_D --device-index 4
    
    # Hear exaggerated PULSE crackle
    python eigenrausch_pyo_main.py preview -v PULSE_CRACKLE --device-index 4

#### Render stems for SD-card players

    eigenrausch_bases/BASE_A.wav, BASE_B.wav, ...
    eigenrausch_micro/MICRO_A.wav, MICRO_B.wav, ...
    eigenrausch_pulse/PULSE_A.wav, PULSE_CRACKLE.wav, ...




----------




NOTE: make sure portaudio is installed

    brew install portaudio libsndfile portmidi liblo
    brew --prefix portaudio
        /opt/homebrew/opt/portaudio

    export CFLAGS="-I/opt/homebrew/opt/portaudio/include \
                   -I/opt/homebrew/opt/libsndfile/include \
                   -I/opt/homebrew/opt/liblo/include \
                   -I/opt/homebrew/opt/portmidi/include"
    
    export LDFLAGS="-L/opt/homebrew/opt/portaudio/lib \
                   -L/opt/homebrew/opt/libsndfile/lib \
                   -L/opt/homebrew/opt/liblo/lib \
                   -L/opt/homebrew/opt/portmidi/lib"

    pip install --no-cache-dir pyo
