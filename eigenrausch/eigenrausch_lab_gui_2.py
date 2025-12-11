"""
eigenrausch_lab_gui.py

Small "Eigenrausch Lab" for interactive listening + visual scopes + spectrums.

- Boots a pyo Server (requires wxPython for GUI windows).
- Instantiates one BASE, one MICRO, and one PULSE variant.
- Opens:
    * Scope window for each layer + combined mix
    * Spectrum window for each layer + combined mix

Run with:

    python eigenrausch_lab_gui.py

Requirements:
    pip install pyo
    pip install wxPython
"""

from pyo import Server, Scope, Spectrum

from eigenrausch_config import SAMPLE_RATE
from eigenrausch_base_layer import EigenBase, BASE_VARIANTS
from eigenrausch_micro_layer import EigenMicro, MICRO_VARIANTS
from eigenrausch_pulse_layer import EigenPulse, PULSE_VARIANTS


# --------------------------------------------------------------------
# CONFIG: choose which variants to inspect in the lab
# --------------------------------------------------------------------

BASE_VARIANT_NAME = "BASE_A"
MICRO_VARIANT_NAME = "MICRO_D"       # good for 50+ ears
PULSE_VARIANT_NAME = "PULSE_CRACKLE"


def build_base_layer(server: Server):
    """Create a BASE layer instance from BASE_VARIANTS."""
    params = BASE_VARIANTS[BASE_VARIANT_NAME]

    base = EigenBase(
        server=server,
        center_freq_hz=params["center_freq_hz"],
        drift_depth_hz=params["drift_depth_hz"],
        drift_period_sec=params["drift_period_sec"],
        amp_lfo_depth=params["amp_lfo_depth"],
        amp_lfo_period_sec=params["amp_lfo_period_sec"],
        # out_db uses default from EigenBase if omitted.
    ).out()

    return base


def build_micro_layer(server: Server):
    """Create a MICRO layer instance from MICRO_VARIANTS."""
    params = MICRO_VARIANTS[MICRO_VARIANT_NAME]

    micro = EigenMicro(
        server=server,
        freq_min_hz=params["freq_min_hz"],
        freq_max_hz=params["freq_max_hz"],
        num_tones=params["num_tones"],
        amp_lfo_freq_min=params["amp_lfo_freq_min"],
        amp_lfo_freq_max=params["amp_lfo_freq_max"],
        noise_db=params["noise_db"],
        tone_db=params["tone_db"],
        # out_db uses default from EigenMicro if omitted.
    ).out()

    return micro


def build_pulse_layer(server: Server):
    """Create a PULSE layer instance from PULSE_VARIANTS."""
    params = PULSE_VARIANTS[PULSE_VARIANT_NAME]

    pulse = EigenPulse(
        server=server,
        freq_min_hz=params["freq_min_hz"],
        freq_max_hz=params["freq_max_hz"],
        pulse_rate_min=params["pulse_rate_min"],
        pulse_rate_max=params["pulse_rate_max"],
        noise_db=params["noise_db"],
        pulse_db=params["pulse_db"],
        # out_db uses default from EigenPulse if omitted.
    ).out()

    return pulse


def main():
    # ----------------------------------------------------------------
    # Set up pyo Server
    # ----------------------------------------------------------------
    s = Server(sr=SAMPLE_RATE, nchnls=2, buffersize=1024, duplex=0)
    s.setVerbosity(0)  # keep console quiet
    s.boot()

    # ----------------------------------------------------------------
    # Build layers
    # ----------------------------------------------------------------
    base = build_base_layer(s)
    micro = build_micro_layer(s)
    pulse = build_pulse_layer(s)

    # Combined signal for monitoring / visualisation
    mix = base.out_sig + micro.out_sig + pulse.out_sig

    # ----------------------------------------------------------------
    # Scopes (time domain)
    # ----------------------------------------------------------------
    # You can tweak 'time' (window length) and 'gain' as needed.
    scope_base = Scope(base.out_sig)
    scope_micro = Scope(micro.out_sig)
    scope_pulse = Scope(pulse.out_sig)
    scope_mix = Scope(mix)

    # ----------------------------------------------------------------
    # Spectrums (frequency domain)
    # ----------------------------------------------------------------
    # size = FFT size, wintype = window type (2 = Hanning).
    spec_base = Spectrum(base.out_sig, size=2048, wintype=2, wintitle="spectrum base")
    spec_micro = Spectrum(micro.out_sig, size=2048, wintype=2, wintitle="spectrum micro")
    spec_pulse = Spectrum(pulse.out_sig, size=2048, wintype=2, wintitle="spectrum pulse")
    spec_mix = Spectrum(mix, size=2048, wintype=2, wintitle="spectrum mix")

    # ----------------------------------------------------------------
    # Start audio + GUI
    # ----------------------------------------------------------------
    s.start()

    print("Eigenrausch Lab running.")
    print(f"  BASE variant : {BASE_VARIANT_NAME}")
    print(f"  MICRO variant: {MICRO_VARIANT_NAME}")
    print(f"  PULSE variant: {PULSE_VARIANT_NAME}")
    print("Scope + Spectrum windows should be visible (requires wxPython).")
    print("Use the pyo GUI window to stop/quit.\n")

    # This opens the main pyo GUI and hands control over to WxPython.
    s.gui(locals())


if __name__ == "__main__":
    main()
