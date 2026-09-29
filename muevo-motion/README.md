# MUEVO — Classic in Motion

Instagram Reels brand film for 무에보 (MUEVO): 1080×1920, 15 s, 30 fps.
The type is kinetic, and the 3D gold ring weaves through the letters.

- `muevo-reel-15s.mp4`: final cut with sound design
- `muevo-reel-15s-silent.mp4`: no audio (use this if you add music inside Instagram)

## Storyboard

| Time | Scene | Copy | Motion |
|---|---|---|---|
| 0.0–3.0 | Ivory | 유행이 / 아닌, | Letters rise in one at a time, and a 3D gold band rolls into "이". A gold strike runs through "유행이", then its fill empties to an outline. The ring then flies toward the camera, and the next scene opens inside its hole. |
| 3.0–6.0 | Ink | 오래 남는 / 클래식의 기준. | Three rows of CLASSIC scroll in opposite directions. The spinning ring and pearls weave through them, and the scene exits through a staggered column wipe. |
| 6.0–8.6 | Champagne | 평생 / 착용할 수 있는 | A 4×3 grid pops in: product photos, a brilliant-cut diamond that draws itself, a pearl, 14K and 18K. Four tiles then flip to new content, and an iris opens to the next scene. |
| 8.6–11.9 | Ink | 클래식한 / 파인주얼리. | Product photos cycle inside a circular portrait. The ring and pearls orbit it in 3D, passing behind and in front. |
| 11.9–15.0 | Ivory | MUEVO / 무에보 | The portrait becomes an ivory disc and expands to fill the screen. The lockup assembles while a white-gold ring grows into the gold one and they link. |

## How it's built

- `index.html` is a deterministic page: `window.seek(t)` fully sets every element for time `t`.
- The rings are Three.js physical materials. Each frame is rendered in two passes with a clipping plane at z = 0. The half behind the type is drawn on the canvas under the text, and the half in front is drawn over it. This is what makes the ring actually go through the letters.
- `render.cjs` drives headless Chromium frame by frame at 60 fps and pipes the frames to ffmpeg. Frame pairs are then blended down to 30 fps, which gives real motion blur.
- `sound.py` synthesizes the synced sound design with numpy: a pad, watch ticks (a "time" motif), bells, whooshes, and a two-ring clink.

## Re-render

```bash
npm install
npm run serve &                      # http://127.0.0.1:8765
node render.cjs full 60 master60.mkv # lossless 60 fps master
python3 sound.py                     # sfx.wav
ffmpeg -i master60.mkv -i sfx.wav -vf "tmix=frames=2,fps=30,format=yuv420p" \
  -c:v libx264 -preset slow -crf 16 -profile:v high -movflags +faststart \
  -c:a aac -b:a 192k -shortest muevo-reel-15s.mp4
```

Fonts: Pretendard (OFL) and Cormorant Garamond (OFL).
