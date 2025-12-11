"""
eigenrausch_lab_gui.py

Small "Eigenrausch Lab" for interactive listening + visual scopes.

- Boots a pyo Server (requires wxPython for GUI windows).
- Instantiates one BASE, one MICRO, and one PULSE variant.
- Opens a Scope window for each layer + a combined scope.

Run with:

    python eigenrausch_lab_gui.py

Make sure:
    pip install wxPython
    pip install pyo
"""

from pyo import Server, Scope

from eigenrausch_config import SAMPLE_RATE, db_to_amp
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

    # BASE_VARIANTS keys expected:
    #   center_freq_hz, drift_depth_hz, drift_period_sec,
    #   amp_lfo_depth, amp_lfo_period_sec
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

    # MICRO_VARIANTS keys expected:
    #   freq_min_hz, freq_max_hz, num_tones,
    #   amp_lfo_freq_min, amp_lfo_freq_max,
    #   noise_db, tone_db
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

    # PULSE_VARIANTS keys expected:
    #   freq_min_hz, freq_max_hz,
    #   pulse_rate_min, pulse_rate_max,
    #   noise_db, pulse_db
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
    # Using default output device; if you want a specific index:
    #   s = Server(sr=SAMPLE_RATE, nchnls=2, buffersize=1024, duplex=0)
    #   s.setOutputDevice(<index>)
    #   s.setVerbosity(0)
    #   s.boot()
    #
    # Here we just boot with default output device.
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
    # Scopes
    # ----------------------------------------------------------------
    # Simple scopes; you can tweak 'time' (window length) and 'gain'
    # to taste if needed (e.g., Scope(mix, time=0.2, gain=2.0)).
    scope_base = Scope(base.out_sig)
    scope_micro = Scope(micro.out_sig)
    scope_pulse = Scope(pulse.out_sig)
    scope_mix = Scope(mix)

    # ----------------------------------------------------------------
    # Start audio + GUI
    # ----------------------------------------------------------------
    s.start()

    print("Eigenrausch Lab running.")
    print(f"  BASE variant : {BASE_VARIANT_NAME}")
    print(f"  MICRO variant: {MICRO_VARIANT_NAME}")
    print(f"  PULSE variant: {PULSE_VARIANT_NAME}")
    print("Scopes windows should be visible (requires wxPython).")
    print("Use the pyo GUI window to stop/quit.\n")

    # This opens the main pyo GUI and hands control over to WxPython.
    s.gui(locals())


if __name__ == "__main__":
    main()
