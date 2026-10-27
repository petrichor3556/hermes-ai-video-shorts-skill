# Remotion: word-by-word captions from `words.json`

Setup: `npx create-video@latest`, 1080x1920, 30 fps. Put `voice.mp3` in `public/` and import `words.json`.

```jsx
import {AbsoluteFill, Audio, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import words from './words.json';

// Group words into sentence pills (split after . ? ! or after 7 words).
const groups = [];
let cur = [];
words.forEach((w) => {
  cur.push(w);
  if (/[.!?]$/.test(w.word) || cur.length >= 7) { groups.push(cur); cur = []; }
});
if (cur.length) groups.push(cur);

export const Captions = () => {
  const t = useCurrentFrame() / useVideoConfig().fps;
  const g = groups.find((x) => t >= x[0].start - 0.05 && t <= x[x.length - 1].end + 0.25);
  if (!g) return null;
  return (
    <div style={{position: 'absolute', top: 1230, left: 60, right: 60, textAlign: 'center'}}>
      <span style={{background: 'rgba(0,0,0,.72)', borderRadius: 24, padding: '18px 28px', fontSize: 52, color: '#fff'}}>
        {g.map((w, i) => (
          <span key={i} style={{color: t >= w.start && t <= w.end ? '#c8f542' : '#fff'}}>{w.word} </span>
        ))}
      </span>
    </div>
  );
};

export const Main = () => (
  <AbsoluteFill style={{background: '#000'}}>
    <Audio src={staticFile('voice.mp3')} />
    {/* one scene component per script line, switched by the same time t */}
    <Captions />
  </AbsoluteFill>
);
```

Set the composition duration to `Math.ceil((lastWord.end + 1) * 30)` frames.

Scene timing: the start of scene N is the `start` of the first word of script line N, so visuals change exactly when the voice starts the line.
Use short transitions (about 10 frames) and keep one idea per scene.
