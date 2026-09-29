import numpy as np, wave
SR = 48000; DUR = 15.0; N = int(SR * DUR)
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)
t_all = np.arange(N) / SR

def add(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR); n = min(len(sig), N - i)
    if n <= 0: return
    gl, gr = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    L[i:i+n] += sig[:n] * gain * gl * 1.414; R[i:i+n] += sig[:n] * gain * gr * 1.414

def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(t / max(a, 1e-4), 1) * np.exp(-t / d)

def lp(x, fc):  # one-pole lowpass
    a = np.exp(-2 * np.pi * fc / SR); y = np.zeros_like(x); s = 0.0
    for i in range(len(x)): s = (1 - a) * x[i] + a * s; y[i] = s
    return y

def bell(f, dur=2.2, bright=1.0):
    n = int(dur * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for ratio, amp, dec in [(1, 1, 1.0), (2.76, .5 * bright, .45), (5.40, .3 * bright, .25), (8.93, .16 * bright, .12), (2.0, .25, .7)]:
        s += amp * np.sin(2 * np.pi * f * ratio * t + rng.random() * 6) * np.exp(-t / (dur * dec * .5))
    return s * np.minimum(t / .002, 1)

def clink(f=2400):  # metal ring contact
    n = int(1.4 * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for ratio, amp, dec in [(1, 1, .5), (1.47, .7, .35), (2.09, .5, .28), (2.95, .35, .18), (3.8, .25, .1)]:
        s += amp * np.sin(2 * np.pi * f * ratio * t) * np.exp(-t / dec)
    return s * np.minimum(t / .0008, 1)

def tick(f=3800, d=.012):
    n = int(.08 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) * .6 + rng.standard_normal(n) * .4) * np.exp(-t / d)

def thump(f0=62, d=.35):
    n = int(1.0 * SR); t = np.arange(n) / SR
    f = f0 * (1 + 1.6 * np.exp(-t / .03)); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t / d) * np.minimum(t / .003, 1)

def whoosh(dur, rise=True, fc0=300, fc1=5000):
    n = int(dur * SR); x = rng.standard_normal(n); t = np.linspace(0, 1, n)
    fc = fc0 * (fc1 / fc0) ** (t if rise else 1 - t)
    # time-varying one-pole lowpass minus a lower one => band-ish
    y = np.zeros(n); z = np.zeros(n); s1 = s2 = 0.0
    for i in range(n):
        a1 = np.exp(-2 * np.pi * fc[i] / SR); a2 = np.exp(-2 * np.pi * fc[i] * .25 / SR)
        s1 = (1 - a1) * x[i] + a1 * s1; s2 = (1 - a2) * x[i] + a2 * s2; y[i] = s1 - s2
    shape = (t ** 2.2) if rise else ((1 - t) ** 1.6 * np.minimum(t / .08, 1))
    return y * shape

# ── pad: A major add9, slow bloom, chorus-detuned sines ──
pad = np.zeros(N)
for f, a in [(110, .5), (164.8, .38), (220, .3), (277.2, .22), (329.6, .2), (493.9, .09), (659.3, .05)]:
    for det in (-.6, .6):
        pad += a * np.sin(2 * np.pi * (f + det * f / 440) * t_all + rng.random() * 6)
padenv = np.clip(t_all / 1.2, 0, 1) * np.clip((DUR - t_all) / 1.4, 0, 1)
# lift on the lockup
padenv *= 1 + .5 * np.clip((t_all - 11.9) / .8, 0, 1)
pad = lp(pad * padenv, 1800)
L += pad * .05; R += pad * .05

# ── watch tick: 2 ticks per second, "time" motif ──
for k in range(0, 24):
    at = .25 + k * .5
    if at > 11.8: break
    add(tick(3600 if k % 2 else 4200), at, .10, -.3 if k % 2 else .3)

# ── impacts / cuts ──
for at, g in [(.22, .55), (3.02, .8), (6.0, .6), (8.58, .7), (11.98, .85)]:
    add(thump(), at, g)

# ── transitions ──
add(whoosh(.5, True, 200, 6000), 2.55, .22)
add(whoosh(.5, True, 300, 7000), 5.25, .16, .3)
add(whoosh(.45, False, 500, 6000), 5.62, .14, -.3)
add(whoosh(.4, True, 250, 5000), 8.2, .16)
add(whoosh(.6, True, 200, 4500), 11.4, .2)

# ── chimes & sparkles ──
A = 440.0
add(bell(A * 2, 2.4), .95, .16, .4)                # ring lands
add(bell(A * 3, 1.6, .6), 1.25, .08, .6)           # pearl
add(whoosh(.35, False, 1500, 9000), 1.45, .10, -.2) # strike swish
add(bell(A * 1.5 * 2, 2.0), 3.85, .12, -.3)        # 오래 남는
add(bell(A * 2 * 1.26, 2.0), 4.05, .10, .3)         # 클래식의 기준
for i, (r, c) in enumerate([(r, c) for r in range(3) for c in range(4)]):
    add(tick(5200 + 400 * ((r + c) % 3), .008), 6.15 + (r + c) * .07 + .02 * i / 12, .07, -.6 + c * .4)
sh = np.zeros(int(1.0 * SR)); ts = np.arange(len(sh)) / SR
for k in range(14):                                 # diamond-draw shimmer
    f = A * 4 * (2 ** (k / 12 * 1.5)); st = int(k * .05 * SR)
    seg = np.sin(2 * np.pi * f * ts[:len(sh) - st]) * np.exp(-ts[:len(sh) - st] / .25) * .3
    sh[st:] += seg
add(sh, 6.5, .07, .2)
for at in (7.35, 7.47, 7.59, 7.71): add(tick(2600, .02), at, .12, 0)
for at in (9.2, 9.75, 10.3, 10.85): add(bell(A * 4, .8, .4), at, .05, (at - 10) / 2)
add(clink(2350), 12.36, .22, -.15)                   # rings meet
add(clink(3100), 12.52, .12, .2)
add(bell(A * 2, 3.0), 12.0, .14)
add(bell(A * 3, 3.0, .5), 12.05, .07, .5)
add(bell(A * 1.5, 3.0, .5), 12.1, .08, -.5)

# ── reverb (noise-IR convolution) ──
def reverb(x, seed, length=2.2):
    n = int(length * SR); r = np.random.default_rng(seed)
    ir = r.standard_normal(n) * np.exp(-np.arange(n) / SR / .55)
    ir = lp(ir, 5000); ir /= np.sqrt((ir ** 2).sum())
    m = len(x) + n - 1; F = 1 << (m - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, F) * np.fft.rfft(ir, F), F)[:len(x)]
Lw, Rw = reverb(L, 1), reverb(R, 2)
L2, R2 = L * .8 + Lw * .35, R * .8 + Rw * .35
fade = np.clip((DUR - t_all) / .6, 0, 1); L2 *= fade; R2 *= fade
pk = max(np.abs(L2).max(), np.abs(R2).max()); g = .89 / pk
out = np.stack([L2 * g, R2 * g], 1)
with wave.open('sfx.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((out * 32767).astype('<i2').tobytes())
print('rms dB', 20 * np.log10(np.sqrt((out ** 2).mean())))
