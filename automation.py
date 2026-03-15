import os
import re
import math
import time
import requests
import subprocess
import urllib.parse
import sys

# ──────────────────────────────────────────────
# ENV
# ──────────────────────────────────────────────

GROQ_API       = os.getenv("GROQ_API")        # free — primary LLM
CLAUDE_API     = os.getenv("CLAUDE_API")       # optional paid fallback
ELEVENLABS_API = os.getenv("ELEVENLABS_API")
PEXELS_API     = os.getenv("PEXELS_API")

VOICE_ID        = "TxGEqnHWrfWFTfGW9XjX"
TARGET_DURATION = 58
WORDS_PER_MIN   = 145
TARGET_WORDS    = int(TARGET_DURATION / 60 * WORDS_PER_MIN)  # ~140

# ──────────────────────────────────────────────
# LOGGING
# ──────────────────────────────────────────────

def log(step: str, msg: str = ""):
    print(f"[{step}] {msg}" if msg else f"[{step}]", flush=True)

# ──────────────────────────────────────────────
# STARTUP VALIDATION
# ──────────────────────────────────────────────

errors = []
if not GROQ_API:
    errors.append("GROQ_API — required (free at console.groq.com)")
if not ELEVENLABS_API:
    errors.append("ELEVENLABS_API — required for voice generation")
if not PEXELS_API:
    errors.append("PEXELS_API — required for video clips")

if errors:
    log("ERROR", "Missing GitHub secrets:")
    for e in errors:
        log("ERROR", f"  • {e}")
    log("ERROR", "Go to repo Settings → Secrets → Actions and add them.")
    sys.exit(1)

if CLAUDE_API:
    log("CONFIG", "LLM: Groq (primary) + Claude (fallback)")
else:
    log("CONFIG", "LLM: Groq only — add CLAUDE_API secret for fallback")

# ──────────────────────────────────────────────
# LLM HELPERS — Groq first, Claude fallback
# ──────────────────────────────────────────────

def _groq(prompt: str, max_tokens: int) -> str:
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API}",
            "Content-Type": "application/json",
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "max_tokens": max_tokens,
            "temperature": 0.85,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


def _claude(prompt: str, max_tokens: int) -> str:
    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": CLAUDE_API,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-6",
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60,
    )
    if not r.ok:
        raise RuntimeError(f"Claude {r.status_code}: {r.text[:200]}")
    return r.json()["content"][0]["text"].strip()


def llm(prompt: str, max_tokens: int = 1200, step: str = "") -> str:
    """Try Groq. If it fails, try Claude if available. Raise if both fail."""
    try:
        return _groq(prompt, max_tokens)
    except Exception as e:
        log(step or "LLM", f"Groq error: {e}")
        if CLAUDE_API:
            log(step or "LLM", "Falling back to Claude...")
            try:
                return _claude(prompt, max_tokens)
            except Exception as e2:
                log(step or "LLM", f"Claude error: {e2}")
                raise RuntimeError(f"Both LLMs failed. Last: {e2}") from e2
        raise RuntimeError(f"Groq failed, no Claude fallback: {e}") from e


# ──────────────────────────────────────────────
# STEP 1 — TITLE
# ──────────────────────────────────────────────

log("TITLE", "Generating...")

title_prompt = """
You are a top YouTube Shorts strategist for US psychology content.
Your titles hit 8-12% CTR because you know exactly what makes Americans 18-35 stop scrolling.

Generate ONE viral psychology title.

HARD RULES:
- Under 55 characters
- Triggers: curiosity gap, self-doubt, social fear, or identity threat
- Plain conversational American English — zero jargon
- Feels personal, like it's calling the viewer out directly
- No "this will change your life" overpromising

PROVEN FORMATS (pick one and adapt):
- Why you [surprising behavior] without realizing it
- The real reason people [universal behavior]
- You're not [label] — you're just [reframe]
- What your [habit] is actually telling you
- The hidden reason you [relatable struggle]

Return ONLY the title. No quotes. No period. No explanation.
"""

title = llm(title_prompt, max_tokens=80, step="TITLE").strip('"\'')
log("TITLE", title)


# ──────────────────────────────────────────────
# STEP 2 — SCRIPT
# ──────────────────────────────────────────────

log("SCRIPT", "Writing...")

script_prompt = f"""
Write a YouTube Shorts voiceover script for a US psychology channel.

TOPIC: {title}
TARGET: exactly {TARGET_WORDS} words (between {TARGET_WORDS - 5} and {TARGET_WORDS + 5})
AUDIENCE: Americans 18-35 who follow therapy TikTok, self-improvement, and psychology content

VOICE: Calm, direct, slightly intense. Like a trusted friend who just figured something out.

TONE RULES:
- Second person (you/your) throughout
- 6th grade reading level
- No science terms. Say "your brain tricks you" not "cognitive dissonance"
- Short sentences, average 8 words each
- One idea per sentence. Never stack two insights.
- Write how people actually talk

STRUCTURE:
1. HOOK (2 sentences) — Start mid-thought with something uncomfortable that makes the viewer feel seen.
   Never start with "Have you ever" or "Did you know".
2. THE INSIGHT (3-4 sentences) — Explain using a metaphor from American daily life:
   work, social media, dating, money, family.
3. THE EXAMPLE (3-4 sentences) — A specific mini-story with one real detail that makes it feel true.
4. THE REFLECTION (2-3 sentences) — Reframe that makes the viewer feel understood not blamed.
   Final line = quiet revelation, not a motivational quote.

BANNED:
- "Have you ever" opener
- "It's okay to"
- "Science shows" / "Studies say" / "Research proves"
- Exclamation marks
- "at the end of the day" / "the thing is" / "here's the deal" / "in today's world"
- The word "journey"

Return ONLY the script. No labels. No scene markers. Plain text only.
"""

script = llm(script_prompt, max_tokens=600, step="SCRIPT")
word_count = len(script.split())
log("SCRIPT", f"{word_count} words")

with open("script.txt", "w") as f:
    f.write(script)


# ──────────────────────────────────────────────
# STEP 3 — SCENE DESCRIPTIONS
# ──────────────────────────────────────────────

log("SCENES", "Building visual descriptions...")

raw_scene_count = max(10, min(15, math.ceil(word_count / 9)))
clip_duration   = round(TARGET_DURATION / raw_scene_count, 2)

scene_prompt = f"""
Split this script into exactly {raw_scene_count} visual scenes for a YouTube Short.

RULES:
- Each scene covers roughly 9 spoken words
- Cover the ENTIRE script in order
- Every scene must be a DISTINCT setting — no two scenes can look the same
- Descriptions must work as stock footage search terms

EXACT FORMAT — use this for every scene:

SCENE_START
Lines: [~9 words from the script this scene covers]
Visual: [one sentence: specific US setting, action, lighting. Photorealistic. No text in frame.]
SCENE_END

Script:
{script}
"""

scene_raw = llm(scene_prompt, max_tokens=2000, step="SCENES")

visuals = []
for block in scene_raw.split("SCENE_START"):
    if "Visual:" in block:
        for line in block.split("\n"):
            if line.strip().startswith("Visual:"):
                visuals.append(line.replace("Visual:", "").strip())
                break

if not visuals:
    log("SCENES", "Parse failed — using built-in fallback visuals")
    fallback_visuals = [
        "person sitting alone at a coffee shop window, city lights at night",
        "close up of hands scrolling a phone, warm lamp light in a bedroom",
        "young man staring at the ceiling in a dark room, soft window light",
        "woman walking alone on an empty city sidewalk at dusk",
        "close up of a face reflected in a car window, emotional expression",
        "person typing a message then deleting it on their phone, kitchen",
        "overhead shot of a person lying on a bed staring up",
        "silhouette of a person at a window watching rain outside",
        "hands wrapped around a coffee mug, soft morning light on a table",
        "person sitting alone on apartment steps at night, streetlight above",
        "close up of eyes staring into the distance, blurred background",
        "person leaning against a wall in a hallway, head slightly down",
    ]
    visuals = (fallback_visuals * math.ceil(raw_scene_count / len(fallback_visuals)))[:raw_scene_count]

log("SCENES", f"{len(visuals)} scenes")


# ──────────────────────────────────────────────
# STEP 4 — PEXELS VIDEO CLIPS
# ──────────────────────────────────────────────

log("PEXELS", "Building search queries...")

query_prompt = f"""
Convert each visual description below into a 2-4 word Pexels stock video search query.
Only keep the physical subject and main action. Remove lighting, mood, and style words.
Short concrete queries work best on Pexels.

Reply with one query per line, numbered. Nothing else.

Visuals:
{chr(10).join(f"{i+1}. {v}" for i, v in enumerate(visuals))}
"""

query_raw = llm(query_prompt, max_tokens=500, step="PEXELS")

queries = []
for line in query_raw.strip().split("\n"):
    clean = re.sub(r"^\d+[\.\)\-\s]+", "", line).strip()
    if clean:
        queries.append(clean)

while len(queries) < len(visuals):
    queries.append("person alone thinking")
queries = queries[:len(visuals)]

log("PEXELS", f"Sample queries: {queries[:4]}")


PEXELS_FALLBACKS = [
    "person thinking",
    "person alone city night",
    "emotional person window",
    "person walking urban",
    "contemplative person indoors",
    "person sitting alone",
]


def pexels_clip(query: str, filename: str, min_dur: int = 4) -> bool:
    url = (
        "https://api.pexels.com/videos/search"
        f"?query={urllib.parse.quote(query)}"
        "&orientation=portrait&per_page=15&size=medium"
    )
    try:
        res = requests.get(url, headers={"Authorization": PEXELS_API}, timeout=15)
        res.raise_for_status()
        videos = res.json().get("videos", [])
    except Exception as e:
        log("PEXELS", f"  API error '{query}': {e}")
        return False

    for v in videos:
        if v.get("duration", 0) < min_dur:
            continue
        vfiles = v.get("video_files", [])
        portrait = [f for f in vfiles if f.get("height", 0) >= f.get("width", 1)]
        ranked = sorted(portrait or vfiles, key=lambda x: x.get("height", 0), reverse=True)
        if not ranked:
            continue
        try:
            r = requests.get(ranked[0]["link"], timeout=45, stream=True)
            with open(filename, "wb") as fh:
                for chunk in r.iter_content(chunk_size=65536):
                    fh.write(chunk)
            if os.path.exists(filename) and os.path.getsize(filename) > 50_000:
                return True
        except Exception as e:
            log("PEXELS", f"  Download error: {e}")
            if os.path.exists(filename):
                os.remove(filename)

    return False


raw_clips = []
min_dur = max(3, math.ceil(clip_duration))

for i, q in enumerate(queries):
    fname = f"raw_{i}.mp4"
    if pexels_clip(q, fname, min_dur=min_dur):
        raw_clips.append(fname)
        log("PEXELS", f"  ✓ {i+1}/{len(queries)}: {q}")
    else:
        downloaded = False
        for fb in PEXELS_FALLBACKS:
            if pexels_clip(fb, fname, min_dur=3):
                raw_clips.append(fname)
                log("PEXELS", f"  ↩ {i+1}/{len(queries)}: fallback '{fb}'")
                downloaded = True
                break
        if not downloaded:
            log("PEXELS", f"  ✗ {i+1}/{len(queries)}: skipped")
    time.sleep(0.3)

if len(raw_clips) < 5:
    log("ERROR", f"Only {len(raw_clips)} clips downloaded — need at least 5.")
    log("ERROR", "Check that PEXELS_API secret is correct and not expired.")
    sys.exit(1)

log("PEXELS", f"{len(raw_clips)} clips ready")


# ──────────────────────────────────────────────
# STEP 5 — VOICE (ElevenLabs)
# ──────────────────────────────────────────────

log("VOICE", "Generating...")

voice_res = requests.post(
    f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
    headers={"xi-api-key": ELEVENLABS_API, "Content-Type": "application/json"},
    json={
        "text": script,
        "model_id": "eleven_flash_v2_5",
        "voice_settings": {
            "stability": 0.45,
            "similarity_boost": 0.80,
            "style": 0.25,
            "use_speaker_boost": True,
        },
    },
    timeout=90,
)

if not voice_res.ok:
    log("ERROR", f"ElevenLabs {voice_res.status_code}: {voice_res.text[:200]}")
    sys.exit(1)

with open("voice.mp3", "wb") as f:
    f.write(voice_res.content)

probe = subprocess.run(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
     "-of", "default=noprint_wrappers=1:nokey=1", "voice.mp3"],
    capture_output=True, text=True,
)
try:
    actual_duration = float(probe.stdout.strip())
except (ValueError, AttributeError):
    actual_duration = TARGET_DURATION
    log("VOICE", "ffprobe parse failed — using target duration")

log("VOICE", f"{actual_duration:.1f}s")


# ──────────────────────────────────────────────
# STEP 6 — PROCESS CLIPS
# ──────────────────────────────────────────────

log("VIDEO", "Processing clips to 9:16...")

per_clip = actual_duration / len(raw_clips)
processed = []

for i, c in enumerate(raw_clips):
    out = f"proc_{i}.mp4"
    cmd = (
        f'ffmpeg -y -i "{c}" '
        f'-vf "crop=ih*9/16:ih,scale=720:1280,setsar=1" '
        f'-t {per_clip:.3f} '
        f'-r 30 -c:v libx264 -preset fast -crf 23 '
        f'-an "{out}"'
    )
    res = subprocess.run(cmd, shell=True, capture_output=True)
    if res.returncode == 0 and os.path.exists(out) and os.path.getsize(out) > 10_000:
        processed.append(out)
    else:
        log("VIDEO", f"  ✗ proc {i}: {res.stderr[-150:].decode(errors='ignore')}")

if not processed:
    log("ERROR", "Zero clips processed. Aborting.")
    sys.exit(1)

log("VIDEO", f"{len(processed)} clips at {per_clip:.2f}s each")


# ──────────────────────────────────────────────
# STEP 7 — CONCAT SILENT VIDEO
# ──────────────────────────────────────────────

log("VIDEO", "Concatenating...")

with open("list.txt", "w") as f:
    for p in processed:
        f.write(f"file '{p}'\n")

concat = subprocess.run(
    "ffmpeg -y -f concat -safe 0 -i list.txt -c copy silent.mp4",
    shell=True, capture_output=True, text=True,
)
if concat.returncode != 0:
    log("ERROR", f"Concat failed: {concat.stderr[-400:]}")
    sys.exit(1)

log("VIDEO", "Silent video ready")


# ──────────────────────────────────────────────
# STEP 8 — SUBTITLES
# ──────────────────────────────────────────────

log("SUBTITLES", "Generating SRT...")

subtitle_prompt = f"""
Generate an SRT subtitle file for this voiceover.

Speech rate: {WORDS_PER_MIN} words per minute
Total duration: {actual_duration:.1f} seconds

RULES:
- 2-4 words per caption line
- Time proportionally by word count
- Capitalize first word only
- No punctuation except commas mid-sentence and a period at sentence end
- Strict SRT format:

1
00:00:00,000 --> 00:00:02,000
Caption text here

2
00:00:02,000 --> 00:00:04,000
Next caption here

Return ONLY the SRT. No markdown fences. No explanation.

Script:
{script}
"""

srt_raw = llm(subtitle_prompt, max_tokens=2500, step="SUBTITLES")
srt_clean = re.sub(r"```[a-zA-Z]*\n?", "", srt_raw).strip()

has_subs = "-->" in srt_clean
if has_subs:
    with open("subtitles.srt", "w", encoding="utf-8") as f:
        f.write(srt_clean)
    log("SUBTITLES", "SRT ready")
else:
    log("SUBTITLES", "Invalid SRT — skipping captions")


# ──────────────────────────────────────────────
# STEP 9 — FINAL RENDER
# ──────────────────────────────────────────────

log("VIDEO", "Final render...")

def build_final(with_subs: bool) -> int:
    if with_subs:
        srt_path = os.path.abspath("subtitles.srt").replace("\\", "/").replace(":", "\\:")
        vf = (
            f"scale=720:1280,"
            f"subtitles='{srt_path}':force_style='"
            "FontName=Arial,FontSize=20,Bold=1,"
            "PrimaryColour=&H00FFFFFF,"
            "OutlineColour=&H00000000,"
            "Outline=2,Shadow=1,"
            "Alignment=2,MarginV=80'"
        )
    else:
        vf = "scale=720:1280"

    cmd = (
        f'ffmpeg -y '
        f'-i silent.mp4 '
        f'-i voice.mp3 '
        f'-vf "{vf}" '
        f'-c:v libx264 -preset fast -crf 22 '
        f'-c:a aac -b:a 128k '
        f'-t {actual_duration:.3f} '
        f'-shortest '
        f'-movflags +faststart '
        f'short.mp4'
    )
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        log("VIDEO", f"FFmpeg stderr: {result.stderr[-400:]}")
    return result.returncode


code = build_final(with_subs=has_subs)

if code != 0 and has_subs:
    log("VIDEO", "Subtitle render failed — retrying without captions")
    code = build_final(with_subs=False)

if code != 0:
    log("ERROR", "Final render failed on both attempts. Aborting.")
    sys.exit(1)

mode = "with captions" if has_subs else "without captions (libass not available)"
log("VIDEO", f"Rendered {mode}")


# ──────────────────────────────────────────────
# STEP 10 — METADATA
# ──────────────────────────────────────────────

log("META", "Writing...")

meta_prompt = f"""
Write YouTube Shorts upload metadata for a US psychology channel targeting viewers 18-35.

Title: {title}
Script opening: {' '.join(script.split()[:30])}...

Output in this EXACT format:

TITLE:
{title}

DESCRIPTION:
[2-3 sentences under 200 chars total. Hook the topic, tease the insight, CTA to follow]

HASHTAGS:
[10 hashtags on one line: mix broad (#psychology #mindset) and niche (#darkpsychology #behaviortok)]

TAGS_CSV:
[20 comma-separated YouTube tags, no # symbol]
"""

meta = llm(meta_prompt, max_tokens=400, step="META")
with open("metadata.txt", "w") as f:
    f.write(meta)

log("META", "metadata.txt saved")


# ──────────────────────────────────────────────
# DONE
# ──────────────────────────────────────────────

size_mb = os.path.getsize("short.mp4") / 1_048_576
log("DONE", f"short.mp4 — {size_mb:.1f} MB | {actual_duration:.1f}s | {word_count} words")
log("DONE", f"Title: {title}")
