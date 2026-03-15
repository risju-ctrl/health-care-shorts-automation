import os
import re
import math
import requests
import json
import subprocess
import urllib.parse
import sys

# ──────────────────────────────────────────────
# ENV / CONFIG
# ──────────────────────────────────────────────

CLAUDE_API     = os.getenv("CLAUDE_API")
ELEVENLABS_API = os.getenv("ELEVENLABS_API")
PEXELS_API     = os.getenv("PEXELS_API")

VOICE_ID        = "TxGEqnHWrfWFTfGW9XjX"   # keep your existing voice
TARGET_DURATION = 58                         # seconds
WORDS_PER_MIN   = 145                        # ElevenLabs pacing at default speed
TARGET_WORDS    = int(TARGET_DURATION / 60 * WORDS_PER_MIN)   # ≈ 140 words

# ──────────────────────────────────────────────
# STARTUP VALIDATION
# ──────────────────────────────────────────────

missing = [name for name, val in [
    ("CLAUDE_API", CLAUDE_API),
    ("ELEVENLABS_API", ELEVENLABS_API),
    ("PEXELS_API", PEXELS_API),
] if not val]

if missing:
    print(f"[ERROR] Missing environment variables: {', '.join(missing)}")
    print("  → Make sure these are set as GitHub repository secrets")
    print("    and referenced in the workflow env: block.")
    sys.exit(1)

# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────

def claude(prompt: str, max_tokens: int = 1200) -> str:
    """Single-turn Claude call. Headers built here so env is always live."""
    headers = {
        "x-api-key": CLAUDE_API,           # read at call-time, never at import
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "claude-sonnet-4-6",      # current model string (no date suffix)
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json=payload,
        timeout=60,
    )
    if not r.ok:
        print(f"[ERROR] Claude API {r.status_code}: {r.text[:300]}")
    r.raise_for_status()
    data = r.json()
    return data["content"][0]["text"].strip()


def log(step: str, msg: str = ""):
    tag = f"[{step}]"
    print(f"{tag} {msg}" if msg else tag)


# ──────────────────────────────────────────────
# STEP 1 — TITLE
# ──────────────────────────────────────────────

log("TITLE", "Generating...")

title_prompt = """
You are a top-performing YouTube Shorts strategist for US psychology content.

Your titles consistently hit 8–12% CTR on Shorts because you understand
what makes American viewers (18–35) stop scrolling.

Generate ONE viral psychology title. Follow every rule:

RULES:
- Under 55 characters including spaces
- Must trigger one of: curiosity gap, self-doubt, social fear, or identity threat
- Written in plain American English — no jargon, no SAT words
- Must feel personal, like it's calling the viewer out directly
- No clickbait that overpromises (avoid "this will change your life")
- Use second-person ("you / your") OR a provocative statement

FORMATS THAT WORK WELL:
- "Why you [do surprising thing] without knowing it"
- "The real reason people [universal behavior]"
- "You're not [label] — you're just [reframe]"
- "What your [habit/reaction] reveals about you"
- "The hidden reason you [relatable struggle]"

Return only the title. No quotes. No explanation.
"""

title = claude(title_prompt, max_tokens=100)
log("TITLE", title)


# ──────────────────────────────────────────────
# STEP 2 — SCRIPT
# ──────────────────────────────────────────────

log("SCRIPT", "Writing...")

script_prompt = f"""
You are writing a YouTube Shorts script for a US psychology channel.
The voice is calm, direct, and slightly intense — like a trusted friend
who just learned something that reframes everything.

TARGET: exactly {TARGET_WORDS} words (±5 words). This fills exactly 58 seconds
at 145 wpm. Count carefully.

TOPIC: {title}

AUDIENCE: Americans 18–35 who follow self-improvement, therapy TikTok,
and psychology content. They respond to relatable moments, not lectures.

TONE RULES:
- Second person ("you / your") throughout
- Plain American English — 6th grade reading level
- No scientific terms (say "your brain tricks you" not "cognitive dissonance")
- Short punchy sentences. Average 8 words per sentence.
- One idea per sentence. Never compound two insights.
- Conversational — write how people actually talk, not how they write

STRUCTURE (follow in order):
1. HOOK (first 2 sentences): State something uncomfortable or surprising
   that makes the viewer feel seen. DO NOT start with "Have you ever".
   Start mid-thought, like you're already in the conversation.
2. THE INSIGHT (3–4 sentences): Explain the psychology behind it simply.
   Use a metaphor from everyday American life (work, dating, social media,
   family, money) to make it concrete.
3. THE EXAMPLE (3–4 sentences): Tell a specific mini-story. A relatable
   scenario. Give it texture — a detail that makes it feel real.
4. THE REFLECTION (final 2–3 sentences): End with a reframe that makes
   the viewer feel understood, not blamed. Last line should land like
   a quiet revelation — not a motivational quote.

FORBIDDEN:
- "Have you ever…" as an opener
- "It's okay to…" (too therapy-speak)
- "Science shows…" or "Studies say…"
- Exclamation marks
- The word "actually" more than once
- Filler phrases: "at the end of the day", "the thing is", "here's the deal"

Return only the script. No scene labels. No parentheticals. Plain text only.
"""

script = claude(script_prompt, max_tokens=500)

word_count = len(script.split())
log("SCRIPT", f"{word_count} words")

with open("script.txt", "w") as f:
    f.write(script)


# ──────────────────────────────────────────────
# STEP 3 — SCENES
# ──────────────────────────────────────────────

log("SCENES", "Breaking into scenes...")

# Calculate scene count based on actual word count so clip math is exact
# Each scene = ~5 spoken words → clips_needed = words / 5
raw_scene_count = max(10, min(16, math.ceil(word_count / 5)))  # 10–16 scenes
clip_duration   = round(TARGET_DURATION / raw_scene_count, 1)  # seconds per clip

scene_prompt = f"""
Break this script into exactly {raw_scene_count} visual scenes.

Rules:
- Each scene covers roughly 5 spoken words of the script
- Scenes must cover the ENTIRE script in order — do not skip any lines
- Every scene needs a distinct visual moment — no two scenes can be the same setting

For each scene output this exact format and nothing else:

SCENE_START
Script Lines: [the 5 or so words from the script this scene covers]
Visual: [one sentence describing what the viewer sees — be specific about
         setting, lighting, and emotional tone. US urban/suburban environments.
         Cinematic, photorealistic style. No text or UI in frame.]
SCENE_END

Script:
{script}
"""

scene_raw = claude(scene_prompt, max_tokens=1800)

# Parse scenes
visuals = []
for block in scene_raw.split("SCENE_START"):
    if "Visual:" in block:
        line = [l for l in block.split("\n") if l.strip().startswith("Visual:")][0]
        visuals.append(line.replace("Visual:", "").strip())

log("SCENES", f"{len(visuals)} scenes parsed")


# ──────────────────────────────────────────────
# STEP 4 — PEXELS VIDEO CLIPS
# (replaces broken Whisk + Grok calls)
# ──────────────────────────────────────────────

log("PEXELS", "Downloading clips...")

def pexels_clip(query: str, filename: str, min_duration: int = 4) -> bool:
    """Download a Pexels vertical video matching query. Returns True on success."""
    url = (
        f"https://api.pexels.com/videos/search"
        f"?query={urllib.parse.quote(query)}"
        f"&orientation=portrait"
        f"&per_page=15"
        f"&size=medium"
    )
    try:
        res = requests.get(url, headers={"Authorization": PEXELS_API}, timeout=15)
        res.raise_for_status()
        videos = res.json().get("videos", [])
    except Exception as e:
        log("PEXELS", f"Search failed for '{query}': {e}")
        return False

    for v in videos:
        # Must be long enough for our clip_duration
        if v.get("duration", 0) < min_duration:
            continue
        # Prefer highest-res portrait file
        files = sorted(
            [f for f in v["video_files"] if f.get("height", 0) >= f.get("width", 1)],
            key=lambda x: x.get("height", 0),
            reverse=True,
        )
        if not files:
            # Fall back to any file
            files = sorted(v["video_files"], key=lambda x: x.get("height", 0), reverse=True)
        link = files[0]["link"]
        try:
            r = requests.get(link, timeout=30)
            with open(filename, "wb") as f:
                f.write(r.content)
            if os.path.getsize(filename) > 100_000:
                return True
        except Exception as e:
            log("PEXELS", f"Download failed: {e}")

    return False


# Build search queries from visuals using Claude (batched, 1 call)
log("PEXELS", "Converting visuals to search queries...")

query_prompt = f"""
Convert each visual description into a short 2–4 word Pexels video search query.
Focus on the physical setting and action. Ignore mood/lighting words.
Pexels works best with simple concrete terms.

Respond with one query per line, numbered, matching the scene order.
No extra text.

Visuals:
{chr(10).join(f"{i+1}. {v}" for i, v in enumerate(visuals))}
"""

query_raw = claude(query_prompt, max_tokens=600)
queries = []
for line in query_raw.strip().split("\n"):
    line = re.sub(r"^\d+[\.\)]\s*", "", line).strip()
    if line:
        queries.append(line)

# Pad / trim to match visuals count
while len(queries) < len(visuals):
    queries.append("person thinking city")
queries = queries[:len(visuals)]

log("PEXELS", f"Queries: {queries}")

raw_clips = []
for i, q in enumerate(queries):
    fname = f"raw_{i}.mp4"
    if pexels_clip(q, fname, min_duration=math.ceil(clip_duration)):
        raw_clips.append(fname)
        log("PEXELS", f"  ✓ Scene {i+1}: {q}")
    else:
        # Fallback query
        fallback = "person alone thinking"
        if pexels_clip(fallback, fname, min_duration=3):
            raw_clips.append(fname)
            log("PEXELS", f"  ↩ Scene {i+1} fallback used")
        else:
            log("PEXELS", f"  ✗ Scene {i+1} skipped")

if len(raw_clips) < 3:
    log("ERROR", f"Only {len(raw_clips)} clips downloaded. Aborting.")
    sys.exit(1)

log("PEXELS", f"{len(raw_clips)} clips ready")


# ──────────────────────────────────────────────
# STEP 5 — VOICE
# ──────────────────────────────────────────────

log("VOICE", "Generating...")

voice_res = requests.post(
    f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
    headers={
        "xi-api-key": ELEVENLABS_API,
        "Content-Type": "application/json",
    },
    json={
        "text": script,
        "model_id": "eleven_flash_v2_5",
        "voice_settings": {
            "stability": 0.45,       # slight variation = more human
            "similarity_boost": 0.80,
            "style": 0.25,           # adds emotional expressiveness
            "use_speaker_boost": True,
        },
    },
    timeout=60,
)
voice_res.raise_for_status()

with open("voice.mp3", "wb") as f:
    f.write(voice_res.content)

# Probe actual audio duration
probe = subprocess.run(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
     "-of", "default=noprint_wrappers=1:nokey=1", "voice.mp3"],
    capture_output=True, text=True,
)
actual_duration = float(probe.stdout.strip()) if probe.stdout.strip() else TARGET_DURATION
log("VOICE", f"Duration: {actual_duration:.1f}s")


# ──────────────────────────────────────────────
# STEP 6 — PROCESS CLIPS (uniform duration, 9:16)
# ──────────────────────────────────────────────

log("VIDEO", "Processing clips...")

# Recalculate per-clip duration based on ACTUAL voice duration
per_clip = actual_duration / len(raw_clips)

processed = []
for i, c in enumerate(raw_clips):
    out = f"proc_{i}.mp4"
    # crop to 9:16 portrait, scale to 720×1280, trim to per_clip, re-encode once
    cmd = (
        f'ffmpeg -y -i "{c}" '
        f'-vf "crop=ih*9/16:ih,scale=720:1280,setsar=1" '
        f'-t {per_clip:.3f} '
        f'-r 30 -c:v libx264 -preset fast -crf 23 '
        f'-an "{out}" 2>/dev/null'
    )
    result = os.system(cmd)
    if result == 0 and os.path.exists(out) and os.path.getsize(out) > 10_000:
        processed.append(out)
    else:
        log("VIDEO", f"  ✗ clip {i} failed to process")

if not processed:
    log("ERROR", "No processed clips. Aborting.")
    sys.exit(1)

log("VIDEO", f"{len(processed)} clips processed at {per_clip:.1f}s each")


# ──────────────────────────────────────────────
# STEP 7 — CONCAT + MIX AUDIO (single FFmpeg pass)
# ──────────────────────────────────────────────

log("VIDEO", "Concatenating...")

with open("list.txt", "w") as f:
    for p in processed:
        f.write(f"file '{p}'\n")

# Concat silent video
concat_result = subprocess.run(
    "ffmpeg -y -f concat -safe 0 -i list.txt -c copy silent.mp4",
    shell=True, capture_output=True, text=True,
)
if concat_result.returncode != 0:
    log("ERROR", concat_result.stderr[-500:])
    sys.exit(1)


# ──────────────────────────────────────────────
# STEP 8 — SUBTITLES (burned-in captions)
# ──────────────────────────────────────────────

log("SUBTITLES", "Generating SRT...")

# Ask Claude to split script into ~3-word caption chunks with timing
subtitle_prompt = f"""
Create SRT subtitles for this script spoken at {WORDS_PER_MIN} words per minute.
Total duration: {actual_duration:.1f} seconds.

Rules:
- 2–4 words per subtitle line (short = readable on mobile)
- Time each line proportionally to word count
- Capitalize first word only, no punctuation except commas and periods at end of sentence
- SRT format exactly: index, timecode (HH:MM:SS,mmm --> HH:MM:SS,mmm), text, blank line

Return only the SRT content. No explanation.

Script:
{script}
"""

srt_content = claude(subtitle_prompt, max_tokens=2000)

# Validate it at least looks like SRT
if "-->" in srt_content:
    with open("subtitles.srt", "w") as f:
        f.write(srt_content)
    has_subs = True
    log("SUBTITLES", "SRT written")
else:
    has_subs = False
    log("SUBTITLES", "SRT generation failed — skipping captions")


# ──────────────────────────────────────────────
# STEP 9 — FINAL RENDER
# ──────────────────────────────────────────────

log("VIDEO", "Final render...")

if has_subs:
    # Burn subtitles with bold white text + black outline (mobile-readable)
    sub_filter = (
        "subtitles=subtitles.srt:force_style='"
        "FontName=Arial,FontSize=22,Bold=1,"
        "PrimaryColour=&H00FFFFFF,"   # white
        "OutlineColour=&H00000000,"   # black outline
        "Outline=2,Shadow=1,"
        "Alignment=2,"                # bottom-center
        "MarginV=60'"                 # lift off bottom edge
    )
    vf = f'scale=720:1280,{sub_filter}'
else:
    vf = "scale=720:1280"

final_cmd = (
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

final_result = subprocess.run(final_cmd, shell=True, capture_output=True, text=True)

if final_result.returncode != 0:
    log("ERROR", final_result.stderr[-800:])
    sys.exit(1)


# ──────────────────────────────────────────────
# STEP 10 — METADATA + DESCRIPTION
# ──────────────────────────────────────────────

log("META", "Writing metadata...")

meta_prompt = f"""
Write YouTube Shorts metadata for this psychology video targeting US viewers 18–35.

Title: {title}

Script summary (first 3 lines):
{chr(10).join(script.split(chr(10))[:3])}

Output in this exact format:

TITLE:
[the title]

DESCRIPTION:
[3 sentences. First hooks with the topic. Second teases the insight.
Third ends with a CTA to follow for more psychology content.
Under 200 characters total — Shorts descriptions get cut off.]

HASHTAGS:
[10 hashtags: mix of broad (#psychology #mindset) and niche
(#darkpsychology #behaviortok #mentalhealth) — one line, space-separated]

TAGS_CSV:
[20 comma-separated tags for YouTube tag field, no # symbol]
"""

meta = claude(meta_prompt, max_tokens=400)

with open("metadata.txt", "w") as f:
    f.write(meta)

log("META", "metadata.txt written")

# ──────────────────────────────────────────────
# DONE
# ──────────────────────────────────────────────

size_mb = os.path.getsize("short.mp4") / 1_048_576
log("DONE", f"short.mp4 ready — {size_mb:.1f} MB | {actual_duration:.1f}s | {word_count} words")
print(f"\nTitle: {title}")
