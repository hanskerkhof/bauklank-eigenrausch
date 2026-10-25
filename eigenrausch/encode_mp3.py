"""
encode_mp3.py

Encode every rendered WAV in dist/EIGENRAUSCH_WAV/{BASE,MICRO,PULSE} to a
constant-bitrate MP3 in dist/EIGENRAUSCH/{BASE,MICRO,PULSE}. Requires ffmpeg.

    python encode_mp3.py
"""

import shutil
import subprocess
import sys

from eigenrausch_config import DIST_DIR, MP3_DIR, MP3_BITRATE_KBPS


def main() -> int:
    if shutil.which("ffmpeg") is None:
        print("ffmpeg not found (brew install ffmpeg)", file=sys.stderr)
        return 1

    wavs = sorted(DIST_DIR.glob("*/*.wav"))
    if not wavs:
        print(f"No WAV files found in {DIST_DIR}. Run the generate task first.")
        return 1

    for wav in wavs:
        out = MP3_DIR / wav.parent.name / f"{wav.stem}.mp3"
        out.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav),
             "-codec:a", "libmp3lame", "-b:a", f"{MP3_BITRATE_KBPS}k", str(out)],
            check=True,
        )
        print(f"{wav.name} -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
