"""Edge TTS voice-over with exact word timings.

Usage:
  pip install edge-tts
  python tts_words.py --text script.txt --voice de-DE-FlorianMultilingualNeural --out out/

Writes out/voice.mp3 and out/words.json: [{"word": "...", "start": 0.12, "end": 0.45}, ...] in seconds.
"""
import argparse
import asyncio
import json
from pathlib import Path

import edge_tts


async def synth(text: str, voice: str, rate: str, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    comm = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary")
    words = []
    with (out / "voice.mp3").open("wb") as audio:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                audio.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start = chunk["offset"] / 10_000_000  # 100 ns units -> seconds
                words.append({"word": chunk["text"], "start": round(start, 3),
                              "end": round(start + chunk["duration"] / 10_000_000, 3)})
    (out / "words.json").write_text(json.dumps(words, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(words)} words, last ends at {words[-1]['end'] if words else 0} s")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True, help="UTF-8 text file with the script")
    ap.add_argument("--voice", default="de-DE-FlorianMultilingualNeural")
    ap.add_argument("--rate", default="+0%", help='speed, e.g. "-5%" or "+10%"')
    ap.add_argument("--out", default="out")
    a = ap.parse_args()
    text = Path(a.text).read_text(encoding="utf-8-sig").strip()
    asyncio.run(synth(text, a.voice, a.rate, Path(a.out)))


if __name__ == "__main__":
    main()
