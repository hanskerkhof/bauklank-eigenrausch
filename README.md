# bauklank-eigenrausch
Audio engine for the artwork Eigenrausch: a sculptural translation of eigengrau into sound. Generates layered fields of drifting noise, perceptual micro-tones, and entropy pulses, with tools for realtime preview, spectral analysis, and multichannel rendering.


## Generating sounds (npm tasks)

Common tasks are available as npm scripts (run from the repository root):

| Task | What it does |
|---|---|
| `npm run setup` | Creates `.venv` (Python 3.11) and installs `pyo` and `wxPython`. Needs `brew install portaudio libsndfile portmidi liblo` first. |
| `npm run generate` | Renders every BASE, MICRO and PULSE variant to `dist/EIGENRAUSCH/`. |
| `npm run list` | Lists all available variants. |
| `npm run lab` | Opens the lab: live scope and spectrum windows for one variant per layer. |

Rendered files end up in:

    dist/EIGENRAUSCH/
    ├── BASE/
    ├── MICRO/
    └── PULSE/

`dist/` is git-ignored, so rendered sounds are never committed.

Renders record in real time and default to 30 seconds per file via `npm run generate`
(13 variants, about 6.5 minutes). Set the length in minutes per run:

    EIGENRAUSCH_DURATION_MIN=10 npm run generate

More tasks will be added to the `scripts` block in `package.json`.
