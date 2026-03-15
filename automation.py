import os
import re
import requests
import subprocess
import sys
import json

# ══════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════

GROQ_API       = os.getenv("GROQ_API")       # primary LLM — free
CLAUDE_API     = os.getenv("CLAUDE_API")      # optional fallback — paid
ELEVENLABS_API = os.getenv("ELEVENLABS_API")  # voice

# ElevenLabs free-tier built-in voices:
#   Adam   pNInz6obpgDQGcFmaJgB  deep authoritative male     ← default
#   Antoni ErXwobaYiN019PkySvjV  confident younger male
#   Rachel 21m00Tcm4TlvDq8ikWAM  calm clear female
#   Domi   AZnzlk1XvdvUeBnXmlld  strong expressive female
VOICE_ID = "pNInz6obpgDQGcFmaJgB"

# ElevenLabs free-tier model — do NOT change unless you upgrade
ELEVENLABS_MODEL = "eleven_turbo_v2_5"

# Target: 58 seconds at 145 wpm = 140 words
TARGET_WORDS = 140

# ══════════════════════════════════════════════════════════
# LOGGING
# ══════════════════════════════════════════════════════════

def log(step: str, msg: str = ""):
    print(f"[{step}] {msg}" if msg else f"[{step}]", flush=True)

# ══════════════════════════════════════════════════════════
# STARTUP VALIDATION
# ══════════════════════════════════════════════════════════

missing = []
if not GROQ_API:       missing.append("GROQ_API       — free at console.groq.com")
if not ELEVENLABS_API: missing.append("ELEVENLABS_API — free at elevenlabs.io")

if missing:
    log("ERROR", "Missing GitHub secrets — add these in repo Settings → Secrets → Actions:")
    for m in missing: log("ERROR", f"  • {m}")
    sys.exit(1)

log("CONFIG", f"Voice: {VOICE_ID} | Model: {ELEVENLABS_MODEL} | Target: {TARGET_WORDS} words")
if CLAUDE_API:
    log("CONFIG", "LLM: Groq (primary) + Claude (fallback)")
else:
    log("CONFIG", "LLM: Groq only")

# ══════════════════════════════════════════════════════════
# LLM — Groq primary, Claude fallback
# ══════════════════════════════════════════════════════════

def _groq(prompt: str, max_tokens: int) -> str:
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API}", "Content-Type": "application/json"},
        json={
            "model": "llama-3.3-70b-versatile",
            "max_tokens": max_tokens,
            "temperature": 0.9,
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


def llm(prompt: str, max_tokens: int = 1000, step: str = "") -> str:
    try:
        out = _groq(prompt, max_tokens)
        return out
    except Exception as e:
        log(step or "LLM", f"Groq failed: {e}")
        if CLAUDE_API:
            log(step or "LLM", "Retrying with Claude...")
            try:
                return _claude(prompt, max_tokens)
            except Exception as e2:
                raise RuntimeError(f"Both LLMs failed. Last error: {e2}") from e2
        raise RuntimeError(f"Groq failed and no fallback set: {e}") from e


# ══════════════════════════════════════════════════════════
# STEP 1 — TITLE
# ══════════════════════════════════════════════════════════

log("TITLE", "Generating...")

TITLE_PROMPT = """
You write titles for a US psychology YouTube Shorts channel that gets millions of views.
Your job is to write ONE title that stops an American 18-35 year old mid-scroll.

WHAT WORKS ON SHORTS:
Titles that trigger an instant emotional reaction — not curiosity alone, but a gut punch.
The best titles make the viewer think "wait... is that me?" before they even tap.

PSYCHOLOGICAL TRIGGERS TO USE (pick the strongest one):
- Identity threat: challenges how they see themselves
- Social exposure: reveals something embarrassing or hidden
- Self-sabotage: shows them they're hurting themselves without knowing
- Blind spot: exposes a pattern they've never noticed
- Reframe: flips something they thought was a flaw into something else

FORMAT RULES:
- Under 52 characters
- No ALL CAPS
- No exclamation marks
- No "this will change your life"
- No vague words like "mindset" or "growth" alone
- Must work as a spoken sentence — say it out loud, it should land

BEST PERFORMING FORMATS:
→ "You're not [X] — you're just [unexpected reframe]"
→ "Why you [behavior] and can't stop"
→ "The real reason you [relatable struggle]"
→ "What [habit/reaction] says about how you were raised"
→ "You're [doing X] and you don't even see it"
→ "Stop calling yourself [label] — here's what's really going on"

TOPIC POOL — rotate through these themes, pick whichever feels freshest:
attachment style, people pleasing, self-sabotage, avoidant behavior,
overthinking, fear of success, childhood wounds, emotional unavailability,
social anxiety, imposter syndrome, validation seeking, inner critic,
fear of abandonment, perfectionism, emotional numbness

Return ONLY the title. No quotes. No period. No explanation.
"""

title = llm(TITLE_PROMPT, max_tokens=80, step="TITLE").strip('"\'').strip(".")
log("TITLE", f'"{title}" ({len(title)} chars)')

# Build a clean filename slug from the title
# e.g. "You're not lazy — you're just scared" -> "youre_not_lazy_youre_just_scared"
slug = title.lower()
slug = re.sub(r"['''\u2018\u2019]", "", slug)   # drop apostrophes
slug = re.sub(r"[^a-z0-9]+", "_", slug)               # non-alphanumeric -> underscore
slug = slug.strip("_")[:60]                            # cap length, trim edges

SCRIPT_FILE = f"{slug}_script.txt"
VOICE_FILE  = f"{slug}_voice.mp3"
META_FILE   = f"{slug}_metadata.txt"
REPORT_FILE = f"{slug}_report.txt"

log("TITLE", f"Slug: {slug}")


# ══════════════════════════════════════════════════════════
# STEP 2 — SCRIPT
# ══════════════════════════════════════════════════════════

log("SCRIPT", "Writing...")

SCRIPT_PROMPT = f"""
You are the head writer for a top US psychology YouTube Shorts channel.
Your scripts consistently hit 85%+ retention because they make people feel deeply understood.

ASSIGNMENT: Write the voiceover script for this Short.

TITLE: {title}
EXACT WORD COUNT REQUIRED: {TARGET_WORDS} words — count every word, hit this number precisely.
At 145 words per minute this = exactly 58 seconds of audio.

═══════════════════════════════════
AUDIENCE PROFILE
═══════════════════════════════════
American, 18-35, mostly grew up online.
They follow: therapy TikTok, self-improvement accounts, true crime, pop psychology.
They're skeptical of motivational fluff but hungry for real insight.
They STOP scrolling when something feels uncomfortably true about themselves.
They SHARE when something articulates something they felt but couldn't name.

═══════════════════════════════════
VOICE & TONE
═══════════════════════════════════
- Second person (you/your) the ENTIRE script — never "people" or "they"
- Sound like a calm, sharp friend talking to you at 11pm — not a lecture
- Plain American English. 6th grade reading level max.
- Short punchy sentences. 6-10 words each. Vary the rhythm.
- NO science terms. Instead of "attachment anxiety" say "that fear of being left"
- NO therapy-speak. Instead of "set boundaries" say "you stop picking up the phone"
- Be specific. Specific = believable. Generic = boring.

═══════════════════════════════════
MANDATORY STRUCTURE
═══════════════════════════════════

[HOOK — first 2 sentences, ~20 words]
Drop the viewer straight into a moment they've lived.
The first sentence must create immediate discomfort or recognition.
Do NOT start with: "Have you ever", "Did you know", "So", "Today".
Start mid-scene — like you already know something about them.

[INSIGHT — 3-4 sentences, ~40 words]
Explain the psychology behind it WITHOUT using clinical language.
Use one concrete metaphor from American everyday life.
Good metaphor sources: your phone, your car, your job, your group chat, dating apps, Netflix.
Each sentence = one idea. Never stack two insights in one sentence.

[STORY — 3-4 sentences, ~45 words]
Tell one ultra-specific mini-scenario that makes it feel real.
Give it a texture detail — a specific app, a specific moment, a specific feeling.
The reader should feel like you're describing THEIR life.
No character names. Keep it "you" the whole time.

[REFRAME — 2 sentences, ~20 words]
Flip the narrative — this isn't a flaw, here's what it actually means.
Make the viewer feel understood, not fixed.
Do NOT end with a motivational quote or advice.
The last line should land like a quiet revelation.

[CTA — 1 sentence, ~15 words]
End with a direct, natural call to action.
It must feel conversational — not like an ad.
Examples of GOOD CTAs:
  "Follow for more and save this — you'll want to come back to it."
  "If this one hit, follow — there's more where that came from."
  "Drop a comment if this is you, and follow for more."
  "Follow if you needed to hear this today."
BANNED CTA phrases: "smash the like button", "don't forget to subscribe", "hit that bell"

═══════════════════════════════════
ABSOLUTE BANS
═══════════════════════════════════
✗ "Have you ever…" as opener
✗ "It's okay to…"
✗ "Science shows…" / "Studies say…" / "Research proves…"
✗ "At the end of the day"
✗ "Here's the thing" / "The thing is"
✗ "In today's world" / "In today's society"
✗ "Journey" / "healing journey" / "your truth"
✗ Exclamation marks — anywhere
✗ More than one use of "actually"
✗ Rhetorical questions mid-script (hook only, if at all)

═══════════════════════════════════
WORD COUNT RULE
═══════════════════════════════════
You MUST write exactly {TARGET_WORDS} words (±3 words maximum).
Count every word before you return the script.
If your count is off, rewrite until it's right.
Short scripts ruin the timing. Do not go under {TARGET_WORDS - 3}.

Return ONLY the plain script text.
No section labels. No parentheticals. No markdown. Just the words to be spoken.
"""

script = llm(SCRIPT_PROMPT, max_tokens=700, step="SCRIPT")

# Strip any labels the model might accidentally add
script = re.sub(r"\[(HOOK|INSIGHT|STORY|REFRAME|CTA)[^\]]*\]\s*", "", script, flags=re.IGNORECASE).strip()

word_count = len(script.split())
log("SCRIPT", f"{word_count} words (target: {TARGET_WORDS})")

# Warn if significantly off target
if word_count < TARGET_WORDS - 10:
    log("SCRIPT", f"WARNING: Script is {TARGET_WORDS - word_count} words short — audio may be under 58s")
elif word_count > TARGET_WORDS + 10:
    log("SCRIPT", f"WARNING: Script is {word_count - TARGET_WORDS} words long — audio may exceed 58s")

with open(SCRIPT_FILE, "w", encoding="utf-8") as f:
    f.write(f"TITLE: {title}\n")
    f.write(f"WORD COUNT: {word_count}\n")
    f.write("─" * 50 + "\n\n")
    f.write(script)

log("SCRIPT", f"{SCRIPT_FILE} saved")


# ══════════════════════════════════════════════════════════
# STEP 3 — VOICE (ElevenLabs)
# ══════════════════════════════════════════════════════════

log("VOICE", "Generating audio...")

voice_payload = {
    "text": script,
    "model_id": ELEVENLABS_MODEL,
    "voice_settings": {
        "stability": 0.40,          # slight natural variation
        "similarity_boost": 0.80,   # stays close to the voice character
        "style": 0.30,              # expressiveness — higher = more emotional range
        "use_speaker_boost": True,  # clarity boost
    },
}

voice_res = requests.post(
    f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
    headers={"xi-api-key": ELEVENLABS_API, "Content-Type": "application/json"},
    json=voice_payload,
    timeout=90,
)

if not voice_res.ok:
    log("ERROR", f"ElevenLabs {voice_res.status_code}: {voice_res.text[:300]}")
    log("ERROR", "Common causes:")
    log("ERROR", "  401 → wrong or expired ELEVENLABS_API key")
    log("ERROR", "  402 → free plan limit hit or voice requires paid plan")
    log("ERROR", "  422 → script too long or contains unsupported characters")
    sys.exit(1)

with open(VOICE_FILE, "wb") as f:
    f.write(voice_res.content)

# Verify the file is real audio (not an error page written as mp3)
if os.path.getsize(VOICE_FILE) < 10_000:
    log("ERROR", f"{VOICE_FILE} is suspiciously small — ElevenLabs likely returned an error body")
    sys.exit(1)

# Get actual audio duration via ffprobe
probe = subprocess.run(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
     "-of", "default=noprint_wrappers=1:nokey=1", VOICE_FILE],
    capture_output=True, text=True,
)
try:
    actual_duration = float(probe.stdout.strip())
    log("VOICE", f"{VOICE_FILE} saved — {actual_duration:.1f}s | {os.path.getsize(VOICE_FILE)//1024}KB")
except (ValueError, AttributeError):
    log("VOICE", f"{VOICE_FILE} saved — {os.path.getsize(VOICE_FILE)//1024}KB (duration unknown)")
    actual_duration = None


# ══════════════════════════════════════════════════════════
# STEP 4 — METADATA
# ══════════════════════════════════════════════════════════

log("META", "Generating metadata...")

META_PROMPT = f"""
Write complete YouTube Shorts upload metadata for a US psychology channel.
Target audience: Americans 18-35. Goal: maximum clicks, saves, and follows.

TITLE: {title}
SCRIPT OPENING: {" ".join(script.split()[:25])}...

OUTPUT THIS EXACT FORMAT — no extra text, no labels other than the ones below:

TITLE:
{title}

DESCRIPTION:
[Write 2 punchy sentences under 180 characters TOTAL.
Sentence 1: Hook — make it sound irresistible to tap.
Sentence 2: CTA — "Follow for more psychology content like this."
No hashtags in the description.]

HASHTAGS:
[15 hashtags on a single line, space-separated.
Mix: broad reach (#psychology #mentalhealth #selfimprovement)
+ niche engagement (#darkpsychology #attachmentstyle #therapytok #behaviortok #mindtok)
+ trending formats (#storytime #didyouknow #learnontiktok)
Start each with #]

TAGS:
[25 comma-separated tags for the YouTube tag field. No # symbol.
Mix keyword types: topic tags, behavior tags, audience tags, question-form tags.
Examples: psychology facts, why you overthink, dark psychology, human behavior,
self improvement, stop people pleasing, attachment theory explained,
emotional intelligence, why am I like this, psychology of behavior]

SUGGESTED UPLOAD TIME:
[Best time to post for US audience engagement — give day and time in ET]

THUMBNAIL HOOK:
[One sentence: what text/image would make the strongest thumbnail for this topic]
"""

meta_raw = llm(META_PROMPT, max_tokens=600, step="META")

with open(META_FILE, "w", encoding="utf-8") as f:
    f.write(meta_raw)

log("META", f"{META_FILE} saved")


# ══════════════════════════════════════════════════════════
# STEP 5 — CONTENT REPORT
# ══════════════════════════════════════════════════════════

log("REPORT", "Writing content report...")

duration_str = f"{actual_duration:.1f}s" if actual_duration else "unknown"

report = f"""
╔══════════════════════════════════════════════════════╗
║           AI PSYCHOLOGY SHORTS — RUN REPORT          ║
╚══════════════════════════════════════════════════════╝

TITLE:        {title}
WORD COUNT:   {word_count} words  (target: {TARGET_WORDS})
AUDIO:        {duration_str}  (target: 58s)
VOICE ID:     {VOICE_ID}
MODEL:        {ELEVENLABS_MODEL}

OUTPUT FILES:
  {SCRIPT_FILE}    — full script with title and word count
  {VOICE_FILE}     — final voiceover audio
  {META_FILE}  — title, description, hashtags, tags

SCRIPT PREVIEW (first 3 sentences):
{". ".join(script.split(". ")[:3])}.

""".strip()

with open(REPORT_FILE, "w", encoding="utf-8") as f:
    f.write(report)

print("\n" + report + "\n")
log("DONE", f"All files ready: {SCRIPT_FILE} | {VOICE_FILE} | {META_FILE} | {REPORT_FILE}")
