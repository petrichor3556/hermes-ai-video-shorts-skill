# ai-video-shorts: skill for Hermes Agent

A [Hermes Agent](https://hermes-agent.nousresearch.com) skill that turns verified facts into vertical 9:16 short videos
(Remotion, Edge TTS with exact word timings, word-by-word captions) and publishes them to Telegram, TikTok,
Instagram Reels and YouTube Shorts only after the owner approves.

## Install

```bash
hermes skills tap add petrichor3556/hermes-ai-video-shorts-skill
hermes skills install ai-video-shorts
```

Or copy `skills/content/ai-video-shorts/` into `~/.hermes/skills/content/`.

Requirements: Python 3.10+, `pip install edge-tts imageio-ffmpeg`, Node.js for Remotion.
Telegram posting needs `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHANNEL` in the environment.

## What is inside

- `SKILL.md`: when to use it, the 9-step procedure, pitfalls, verification
- `scripts/tts_words.py`: voice-over plus `words.json` with start/end of every word
- `scripts/compress_for_upload.py`: small h264/aac upload copy (under 10 MB)
- `scripts/tg_post_video.py`: one Telegram post (video + HTML caption up to 1024 characters), edit, length check
- `references/remotion-captions.md`: caption component driven by `words.json`

No credentials are stored in this repository.

## License

MIT
