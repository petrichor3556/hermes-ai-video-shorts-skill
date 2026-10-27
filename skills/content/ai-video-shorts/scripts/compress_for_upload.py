"""Re-encode a video to a small, widely compatible upload copy (h264/aac, 30 fps, yuv420p).

Usage:
  python compress_for_upload.py in.mp4 out.mp4 [--crf 27] [--max-mb 10]

Uses ffmpeg from PATH, or the one bundled with `pip install imageio-ffmpeg`.
Raises the CRF in steps until the file is below --max-mb.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def ffmpeg_path() -> str:
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        sys.exit("ffmpeg not found: install it or `pip install imageio-ffmpeg`")


def encode(src: Path, dst: Path, crf: int) -> None:
    subprocess.run(
        [ffmpeg_path(), "-y", "-i", str(src), "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
         "-r", "30", "-crf", str(crf), "-preset", "slow", "-c:a", "aac", "-ar", "44100", "-ac", "2", "-b:a", "128k",
         "-movflags", "+faststart", str(dst)],
        check=True, capture_output=True,
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--crf", type=int, default=27)
    ap.add_argument("--max-mb", type=float, default=10)
    a = ap.parse_args()
    crf = a.crf
    while True:
        encode(Path(a.src), Path(a.dst), crf)
        size = Path(a.dst).stat().st_size / 1024 / 1024
        print(f"crf {crf}: {size:.1f} MB")
        if size <= a.max_mb or crf >= 36:
            break
        crf += 2


if __name__ == "__main__":
    main()
