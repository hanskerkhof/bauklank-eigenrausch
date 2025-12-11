"""
eigenrausch_base_pyo.py

Generate and preview "Eigenrausch" BASE, MICRO and PULSE sounds using pyo.

LAYERS
------
- BASE  : eigengrau-style band-limited noise with slow spectral drift + breathing.
- MICRO : high-frequency micro-tones (tinnitus-like), appearing and fading
          via random low-frequency modulation.
- PULSE : irregular, short noise bursts (clicky/pulse-like energy) sitting inside
          a very quiet noise bed.

FEATURES
--------
1. PREVIEW
   - preview : preview any variant (BASE_*, MICRO_*, PULSE_*) in realtime.
     Example:
       python eigenrausch_base_pyo.py preview -v BASE_A
       python eigenrausch_base_pyo.py preview -v MICRO_D
       python eigenrausch_base_pyo.py preview -v PULSE_CRACKLE

2. RENDER
   - render      : render a single variant to WAV (any BASE_*, MICRO_*, PULSE_*).
   - render_all  : render all BASE + MICRO + PULSE variants in one run.
     Example:
       python eigenrausch_base_pyo.py render -v BASE_B
       python eigenrausch_base_pyo.py render -v MICRO_C
       python eigenrausch_base_pyo.py render_all

   All render operations record in realtime (e.g. 2 min = ~2 min wall clock).
   Use a small DURATION_MIN (in eigenrausch_config.py) while designing,
   then bump up for final stems.

3. VARIANT LISTING
   - list : print all available variants grouped by layer.
     Example:
       python eigenrausch_base_pyo.py list

REQUIREMENTS
------------
- Python 3.x (3.11 recommended for pyo 1.0.5 on macOS ARM)
- pyo (`pip install pyo`)
"""

import argparse

from eigenrausch_base_layer import (
    BASE_VARIANTS,
    preview_base_variant,
    render_base_variant,
    render_all_base_variants,
)
from eigenrausch_micro_layer import (
    MICRO_VARIANTS,
    preview_micro_variant,
    render_micro_variant,
    render_all_micro_variants,
)
from eigenrausch_pulse_layer import (
    PULSE_VARIANTS,
    preview_pulse_variant,
    render_pulse_variant,
    render_all_pulse_variants,
)


# ---------------------------------------------------------
# Helpers: combined variant mapping & error reporting
# ---------------------------------------------------------


def get_layer_for_variant(variant_name: str) -> str:
    """
    Return which layer a variant belongs to: 'BASE', 'MICRO', or 'PULSE'.

    Raises a ValueError with a combined list of all variants if the variant
    name is not found in any layer.
    """
    if variant_name in BASE_VARIANTS:
        return "BASE"
    if variant_name in MICRO_VARIANTS:
        return "MICRO"
    if variant_name in PULSE_VARIANTS:
        return "PULSE"

    # Unknown variant: build a single, unified error message.
    base_list = ", ".join(sorted(BASE_VARIANTS.keys()))
    micro_list = ", ".join(sorted(MICRO_VARIANTS.keys()))
    pulse_list = ", ".join(sorted(PULSE_VARIANTS.keys()))
    raise ValueError(
        f"Unknown variant '{variant_name}'.\n"
        f"Available variants:\n"
        f"  BASE : {base_list}\n"
        f"  MICRO: {micro_list}\n"
        f"  PULSE: {pulse_list}\n"
    )


def list_all_variants() -> None:
    """Print all available variants grouped by layer."""
    print("Available Eigenrausch variants:\n")

    print("  BASE variants:")
    for name in sorted(BASE_VARIANTS.keys()):
        print(f"    - {name}")

    print("\n  MICRO variants:")
    for name in sorted(MICRO_VARIANTS.keys()):
        print(f"    - {name}")

    print("\n  PULSE variants:")
    for name in sorted(PULSE_VARIANTS.keys()):
        print(f"    - {name}")

    print()


def render_all_layers(device_index: int | None = None) -> None:
    """Render all BASE, MICRO and PULSE variants in one run."""
    render_all_base_variants(device_index=device_index)
    render_all_micro_variants(device_index=device_index)
    render_all_pulse_variants(device_index=device_index)


# ---------------------------------------------------------
# CLI
# ---------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Eigenrausch BASE + MICRO + PULSE sound generator using pyo.",
        usage="%(prog)s {preview,render,render_all,list} [-h] [-v VARIANT] [--device-index DEVICE_INDEX]",
    )

    parser.add_argument(
        "mode",
        choices=[
            "preview",     # preview any variant
            "render",      # render a single variant
            "render_all",  # render all variants (BASE + MICRO + PULSE)
            "list",        # list all variants
        ],
        help=(
            "preview     : listen to a variant (BASE_*, MICRO_*, PULSE_*) in realtime.\n"
            "render      : render a single variant to WAV.\n"
            "render_all  : render all BASE + MICRO + PULSE variants.\n"
            "list        : list all available variants.\n"
        ),
    )

    parser.add_argument(
        "-v",
        "--variant",
        default="BASE_A",
        help=(
            "Name of variant to use.\n"
            "Accepted values include:\n"
            f"  BASE_*  ({', '.join(sorted(BASE_VARIANTS.keys()))})\n"
            f"  MICRO_* ({', '.join(sorted(MICRO_VARIANTS.keys()))})\n"
            f"  PULSE_* ({', '.join(sorted(PULSE_VARIANTS.keys()))})\n"
            "Ignored when mode is 'render_all' or 'list'."
        ),
    )

    parser.add_argument(
        "--device-index",
        type=int,
        default=None,
        help=(
            "PortAudio output device index to use.\n"
            "If not provided, uses the system default output device.\n"
            "Use your pyo device test / pa_list_devices() to inspect devices."
        ),
    )

    args = parser.parse_args()

    mode = args.mode
    variant = args.variant
    device_index = args.device_index

    if mode == "list":
        list_all_variants()
        return

    if mode == "render_all":
        render_all_layers(device_index=device_index)
        return

    # For preview / render, we need to know which layer this variant belongs to.
    layer = get_layer_for_variant(variant)

    if mode == "preview":
        if layer == "BASE":
            preview_base_variant(variant, device_index=device_index)
        elif layer == "MICRO":
            preview_micro_variant(variant, device_index=device_index)
        elif layer == "PULSE":
            preview_pulse_variant(variant, device_index=device_index)
        else:
            raise RuntimeError(f"Unsupported layer '{layer}' for preview.")

    elif mode == "render":
        if layer == "BASE":
            render_base_variant(variant, device_index=device_index)
        elif layer == "MICRO":
            render_micro_variant(variant, device_index=device_index)
        elif layer == "PULSE":
            render_pulse_variant(variant, device_index=device_index)
        else:
            raise RuntimeError(f"Unsupported layer '{layer}' for render.")
    else:
        # Should never happen because argparse restricts choices
        raise RuntimeError("Unknown mode (this should not happen).")


if __name__ == "__main__":
    main()
