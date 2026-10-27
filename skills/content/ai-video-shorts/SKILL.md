---
name: ai-video-shorts
description: Make vertical 9:16 short videos from verified facts (Remotion + Edge TTS with exact word timings + word-by-word captions) and publish them to Telegram, TikTok, Instagram Reels and YouTube Shorts after the owner approves.
version: 1.0.0
author: petrichor3556
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [video, shorts, remotion, tts, telegram, tiktok, instagram, youtube, content]
    requires_toolsets: [terminal]
required_environment_variables:
  - name: TELEGRAM_BOT_TOKEN
    prompt: Telegram bot token (from @BotFather)
    help: Needed only to post to a Telegram channel or to send drafts to the owner.
    required_for: Telegram publishing
  - name: TELEGRAM_CHANNEL
    prompt: Channel username, e.g. @my_channel
    required_for: Telegram publishing
---

# AI Video Shorts

Pipeline for a daily news or tips channel: find a topic, verify the facts, write a short script, voice it,
render a 9:16 video, write the posts, show everything to the owner, publish only after an explicit "publish".

## When to Use

- The owner asks for a short vertical video (30-60 s) about an AI news item, tool, or tip.
- A scheduled daily run must prepare an episode and send a draft for approval.
- Do NOT use it to publish without approval, to give investment advice, or to copy other people's posts or footage.

## Quick Reference

| Step | Tool | Output |
|------|------|--------|
| Facts | web search + fetch primary sources | `facts_NN.md` with links, 2 sources per number |
| Voice + timings | `scripts/tts_words.py` | `voice.mp3` + `words.json` (start/end of each word) |
| Video | Remotion project (see `references/remotion-captions.md`) | `episode.mp4`, 1080x1920, 30 fps |
| Upload copy | `scripts/compress_for_upload.py` | `episode_upload.mp4`, under 10 MB |
| Telegram | `scripts/tg_post_video.py` | one post: video + caption up to 1024 visible chars |
| Other platforms | browser automation, owner stays logged in | TikTok, Instagram (9:16 crop), YouTube Shorts |

## Procedure

1. **Pick one topic.** Search for items from the last 24-48 hours. Skip topics already published (check the posts folder).
2. **Verify facts.** Every number, date and name needs two independent sources, ideally a primary one (official blog, filing, docs).
   Unconfirmed facts are dropped or marked "per media reports". Save facts and links to `facts_NN.md`.
3. **Write the script.** 6-8 short lines, about 40-50 seconds, plain spoken language, numbers written as words for TTS.
   Last line points to the channel for sources. Add pronunciation overrides for English words and names (spell them phonetically in the TTS text).
4. **Voice with timings.** `python scripts/tts_words.py --text script.txt --voice de-DE-FlorianMultilingualNeural --out out/`
   (Edge TTS voices are multilingual; pick one the owner approved and keep it). It writes `voice.mp3` and `words.json`.
5. **Build the video.** Remotion composition, black background with one accent color, word-by-word captions
   (pill with the spoken word highlighted), one visual per script line (cards, bars, source chips), progress bar.
   Keep captions inside the safe zone (about y = 1230 px from top on a 1920 px canvas) so app UI does not cover them.
6. **Render and compress.** `npx remotion render <Composition> out/episode.mp4`, then
   `python scripts/compress_for_upload.py out/episode.mp4 out/episode_upload.mp4`.
   Check with ffprobe: duration, size, h264/aac, 1080x1920.
7. **Write posts.**
   - Telegram: ONE post = video + caption. Bold title, 4-6 bullets, hyperlinks embedded in words, no keycap emoji (use "1."),
     footer is only the channel name linking to the channel. Check with `python scripts/tg_post_video.py check caption.html`.
   - TikTok / Instagram / YouTube: short description, hashtags, link to the channel and the contact handle.
8. **Show the owner before publishing.** Send the compressed video and the texts (facts with sources, caption) to the owner's private chat
   or the current chat. Wait for an explicit "publish". Approval for one episode does not carry over to the next.
9. **Publish.** Telegram through the Bot API script. For other platforms use browser automation on the owner's already-logged-in session;
   never type passwords or solve captchas, ask the owner to do it. Instagram: pick the 9:16 crop. Mark AI-generated content where the platform asks.

## Pitfalls

- **UTF-8 BOM** in caption files shifts Telegram link offsets by one character. Read captions with `utf-8-sig`; write files without BOM.
- **Custom (premium) emoji** cannot be sent by a bot into a channel (Telegram replaces them with a fallback). Add them by editing the post from the owner's own premium account, or use normal emoji.
- **Cyrillic Windows paths** break PyTorch and espeak based TTS; keep models and data in an ASCII path.
- **Edge TTS** returns word timings only with `boundary="WordBoundary"`; default is sentence boundaries.
- **Browser file upload** is often limited to 10 MB, hence the compressed upload copy.
- **Instagram** defaults to a non-9:16 crop; always choose 9:16 in the crop step. Escape in the crop dialog triggers "discard post".
- **Finance news**: state facts only, say it is not investment advice, never forecast prices.
- **Do not leak secrets**: tokens live in environment variables or a `.env` that is never committed or echoed.

## Verification

- `words.json` covers the whole script and the last word ends before the audio ends.
- The rendered video is 1080x1920, plays with sound, and captions are readable inside the safe zone.
- Caption check passes (up to 1024 visible characters) and links point to the intended pages.
- The owner approved this exact episode in the current conversation before anything was posted.
