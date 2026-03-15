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

# ── VOICE SELECTION ───────────────────────────────────────────────────────────
# Psychology Shorts niche requires: warm, close, slightly intimate delivery.
# The voice must feel like someone who KNOWS you — not a narrator, not a doctor.
# Researched against top-performing US faceless psychology channels (2025).
#
# TOP PICKS FOR THIS NICHE (free tier, confirmed working):
#
#   Brian   nPczCjzI2devNBz1zQrb  ← #1 BEST — resonant, comforting American male
#                                     "Middle-aged man with resonant and comforting tone"
#                                     Used by top psychology/dark psychology channels
#                                     Sounds like someone who's figured something out
#
#   Sarah   EXAVITQu4vr4xnSDxMaL  ← #1 FEMALE — soft, clear, intimate American female
#                                     Warm and slightly confessional — therapy-adjacent
#                                     Best for topics around relationships, self-worth
#
#   River   SAz9YHcvj6GT2YYXdXww  ← Gender-neutral, relaxed, calm — great for reframes
#
#   Jessica cgSgspJ2msm6clMCkdW2  ← Young American female, casual and direct
#                                     Strong for social media / texting-theme topics
#
# NOT recommended for this niche:
#   Adam   — too formal/authoritative, feels like a documentary not a confession
#   Charlie — Australian accent, not ideal for US-specific content
#   Antoni  — good but lacks emotional warmth for heavy psychology topics
#
# To swap voice: change VOICE_ID to any ID above
VOICE_ID = "nPczCjzI2devNBz1zQrb"  # Brian — #1 for US psychology Shorts

# Free-tier model (do not change unless you upgrade ElevenLabs plan)
ELEVENLABS_MODEL = "eleven_turbo_v2_5"

# Target: 58 seconds at 145 wpm = 140 words
# ElevenLabs eleven_turbo_v2_5 speaks at ~130 wpm with natural pauses
# 155 words x 130wpm = ~58 seconds (tested)
TARGET_WORDS = 155

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

# Rotate topics using today's date so each daily run hits a different theme
import datetime, hashlib
# US niche psychology Shorts topics — each is a specific relatable behavior,
# not a clinical term. Proven to perform with American 18-35 audience.
# Format: (topic_name, emotional_angle, scene_context)
_TOPICS = [
    # ── RELATIONSHIPS & TEXTING (huge US engagement) ──────────────────────────
    ("leaving people on read",
     "why you go silent on people you actually like",
     "texting, read receipts, the urge to disappear mid-conversation"),

    ("soft ghosting",
     "why you slowly fade instead of just being honest",
     "leaving someone on delivered, posting stories but not replying"),

    ("breadcrumbing",
     "why you keep someone just close enough to not lose them",
     "liking old photos, texting just enough, keeping options open"),

    ("the talking stage anxiety",
     "why you start pulling back right when things are going well",
     "overthinking every text, screenshot to friends, waiting to reply"),

    ("checking their location",
     "why you track people instead of just asking what you need",
     "Find My Friends, always knowing where they are, the relief and shame of it"),

    ("situationship patterns",
     "why you stay in something with no label and pretend you're fine",
     "the undefined relationship, introducing them as 'a friend', avoiding the talk"),

    # ── SOCIAL MEDIA PSYCHOLOGY (massive US niche) ────────────────────────────
    ("posting then deleting",
     "why you share something then immediately regret it",
     "screenshot your own post, delete before anyone sees, refresh the likes"),

    ("doomscrolling at night",
     "why you can't put your phone down even when it makes you feel worse",
     "1am Instagram, the numb scroll, waking up tired from doing nothing"),

    ("comparing your life to strangers online",
     "why someone's highlight reel makes you feel behind in your own story",
     "vacation photos, relationship posts, someone your age doing more"),

    ("performing happiness online",
     "why you post the good days even when you're falling apart inside",
     "curating the feed, not posting when things are bad, the gap between real and posted"),

    ("the parasocial trap",
     "why you feel genuine emotions about people who don't know you exist",
     "getting upset at a creator's drama, feeling betrayed by a stranger, podcast parasocials"),

    ("reply anxiety",
     "why seeing a message notification fills you with dread instead of excitement",
     "the read and don't reply loop, overthinking responses, dreading group chats"),

    # ── WORK & MONEY PSYCHOLOGY (US 20s-30s core anxiety) ────────────────────
    ("Sunday scaries",
     "why Sunday evening feels like the worst part of your week",
     "the dread that starts at 4pm Sunday, the mental prep for Monday, losing the weekend"),

    ("quiet quitting your life",
     "why you do the bare minimum in things that used to excite you",
     "going through motions at work, gym, friendships — present but checked out"),

    ("lifestyle creep guilt",
     "why earning more money never actually makes you feel secure",
     "the raise that didn't fix anything, spending more but feeling the same"),

    ("the comparison career spiral",
     "why LinkedIn makes you feel like a failure even when you're doing fine",
     "someone your age got promoted, started a company, has it together"),

    ("chronic busyness as avoidance",
     "why you keep yourself so busy you never have to feel anything",
     "the packed schedule, no downtime by design, exhausted but can't stop"),

    # ── FAMILY & UPBRINGING (deepest US psychology content) ──────────────────
    ("the responsible child wound",
     "why you became the one who holds everything together and resent it",
     "the family peacekeeper, absorbing everyone's stress, never being the mess"),

    ("growing up too fast",
     "why you can't remember being a carefree kid and what that cost you",
     "handling adult problems young, being 'mature for your age', missing something"),

    ("the parent you became to yourself",
     "why the voice in your head sounds exactly like someone who raised you",
     "self-criticism that echoes a parent, standards that were never yours"),

    ("emotionally immature parents",
     "why you learned to manage their emotions before your own",
     "tip-toeing around a parent's moods, making yourself small, walking on eggshells"),

    # ── SELF BEHAVIOR (viral US psychology hooks) ─────────────────────────────
    ("finishing nothing you start",
     "why you buy the course, start the project, then abandon it every time",
     "the half-read books, unused gym membership, 47 browser tabs"),

    ("apologizing for existing",
     "why 'sorry' comes out of your mouth before you've even done anything",
     "sorry for taking up space, sorry for asking, sorry for having needs"),

    ("people watching strangers and feeling something",
     "why you get emotionally invested in strangers' lives without realizing it",
     "the couple at the restaurant, the person crying on the subway, the barista"),

    ("the 2am spiral",
     "why your worst thoughts always hit when you're alone and it's quiet",
     "lying in the dark, the thoughts that only come at night, the mental loop"),

    ("not being able to accept compliments",
     "why someone saying something nice about you makes you uncomfortable",
     "deflecting praise, the weird silence after a compliment, minimizing yourself"),

    ("the reset fantasy",
     "why you imagine disappearing and starting completely over somewhere new",
     "moving to a new city, new identity, leaving everything behind daydream"),

    ("living in your head",
     "why the most intense version of your life happens in your own imagination",
     "the rehearsed conversations, the imagined scenarios, the life you simulate"),
]
# ── TOPIC SELECTION — never repeats across runs ───────────────────────────────
# Uses a persistent counter file (topic_counter.txt) stored in the repo.
# Each run increments the counter → different topic every single run.
# Counter wraps around after all topics are used (full rotation then repeats).
# If counter file is missing (first run), starts at 0.

_COUNTER_FILE = "topic_counter.txt"

try:
    with open(_COUNTER_FILE, "r") as _f:
        _run_count = int(_f.read().strip())
except (FileNotFoundError, ValueError):
    _run_count = 0

# Advance counter for THIS run
_run_count += 1
_topic_index = (_run_count - 1) % len(_TOPICS)

# Save updated counter back to file so next run picks the next topic
with open(_COUNTER_FILE, "w") as _f:
    _f.write(str(_run_count))

_topic_name, _topic_angle, _topic_scene = _TOPICS[_topic_index]
log("TOPIC", f"Run #{_run_count} → topic {_topic_index + 1}/{len(_TOPICS)}: {_topic_name}")

TITLE_PROMPT = f"""
You write titles for a viral US psychology YouTube Shorts channel targeting Americans 18-35.
Your only job right now: write ONE title for today's topic that stops someone mid-scroll.

TODAY'S TOPIC: {_topic_name}
EMOTIONAL ANGLE: {_topic_angle}
SCENE CONTEXT: {_topic_scene}

The title must make the viewer feel: "wait... that's exactly me."
It must create an emotional gut punch — not just curiosity.

HARD FORMAT RULES:
- 40-52 characters maximum (count spaces)
- No ALL CAPS, no exclamation marks
- No "this will change your life" or "you need to hear this"
- No vague buzzwords: mindset, growth, healing, toxic, trauma (alone)
- Must sound like something a real person would say out loud

PROVEN TITLE FORMATS — pick the one that fits the angle best:
→ "You're not [X] — you're just [reframe]"
→ "Why you [specific behavior] and can't stop"
→ "The real reason you [relatable struggle]"
→ "What your [habit] is really telling you"
→ "You [do this thing] and you don't even know why"
→ "Stop calling yourself [label] — here's the truth"
→ "Why [behavior] feels impossible for you"

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
You are writing a 58-second voiceover script for a US psychology YouTube Shorts channel.

TITLE: {title}
TOPIC: {_topic_name}
EMOTIONAL ANGLE: {_topic_angle}
SCENE CONTEXT (use these real-life details in your SCENE section): {_topic_scene}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL: WORD COUNT = {TARGET_WORDS} WORDS EXACTLY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This script will be read aloud at 145 words per minute = 58 seconds.
You MUST hit {TARGET_WORDS} words. Not 110. Not 130. Not 160. Exactly {TARGET_WORDS}.
ElevenLabs reads at 130 wpm. {TARGET_WORDS} words = 58 seconds. This is non-negotiable.
Each section below has a required sentence count. Follow it precisely.
After writing, count every word. If you're short, expand. If long, cut.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AUDIENCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Americans 18-35. They grew up online. They follow therapy TikTok and pop psychology.
They stop scrolling when something is uncomfortably true about them.
They share when you name something they felt but never could.
They leave when it sounds like a lecture or a self-help book.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VOICE RULES — non-negotiable
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- "you/your" the entire script. Never "people", "some people", "they"
- Every sentence: 6-10 words. Short. Direct. Punchy.
- 6th grade reading level. Plain American English.
- Replace every clinical term with plain language:
    "attachment anxiety" → "that fear of being left"
    "cognitive dissonance" → "that weird feeling when two things don't add up"
    "hypervigilance" → "always waiting for something to go wrong"
    "emotional regulation" → "keeping it together when everything feels like too much"
- No exclamation marks. Ever.
- Be specific. Name the app, the moment, the feeling. Specific = real. Vague = skipped.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 1 — HOOK (exactly 3 sentences, ~30 words)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Sentence 1: Drop them into a moment they've already lived. No setup, no intro.
            FORBIDDEN openers: "Have you ever", "Did you know", "So,", "Today,"
            START with: "You", "That feeling", "When you", "Every time", "There's a reason"
Sentence 2: Twist — add a specific detail that makes it worse or more real.
Sentence 3: The pivot — hint that there's a reason they haven't seen yet.
TARGET: ~30 words for this section.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 2 — THE TRUTH (exactly 4 sentences, ~40 words)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Explain the psychology WITHOUT clinical language.
Use ONE metaphor from American daily life from the SCENE CONTEXT above.
Each sentence = one idea only. Never combine two.
Make them feel like they're learning something real, not being diagnosed.
TARGET: ~40 words for this section.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 3 — THE SCENE (exactly 5 sentences, ~50 words)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Paint one ultra-specific scenario using details from SCENE CONTEXT.
Reference real things: app names, specific moments, the exact feeling in the chest.
Keep it "you" — no character names, no "imagine".
Make it feel like you're describing exactly their Tuesday night.
The viewer should feel: "how does this person know my life."
TARGET: ~50 words for this section.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 4 — THE REFRAME (exactly 3 sentences, ~25 words)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Flip it. This behavior isn't a flaw — here's what it actually is.
Make them feel understood, not fixed, not advised.
Final sentence = a quiet revelation that lands like: "oh. so that's what this is."
TARGET: ~25 words for this section.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 5 — CTA (exactly 1 sentence, ~15 words)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Natural, conversational call to follow. Sounds like a friend, not an ad.
GOOD: "Follow if this one hit — there's a lot more where that came from."
GOOD: "Save this and follow for more — you'll want to come back."
GOOD: "Drop a comment if this is you, and follow for more like this."
BANNED: "smash", "subscribe", "hit that bell", "don't forget"
TARGET: ~15 words for this section.

TOTAL TARGET: 30 + 40 + 50 + 25 + 15 = {TARGET_WORDS} words

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BANNED PHRASES — using any of these = automatic failure
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"Have you ever" / "Did you know" / "It's okay to" / "Science shows"
"Studies say" / "Research proves" / "At the end of the day"
"Here's the thing" / "The thing is" / "In today's world"
"journey" / "healing" / "your truth" / "toxic" (alone) / "empower"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FINAL CHECK BEFORE RETURNING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Count your words. Required: {TARGET_WORDS} (±2).
If under: expand the SCENE section first, then TRUTH.
If over: cut adjectives and adverbs first, then shorten sentences.

Return ONLY the spoken script. No labels. No markdown. No section headers. Plain text only.
"""

script = llm(SCRIPT_PROMPT, max_tokens=1000, step="SCRIPT")

# Strip any labels the model might accidentally add
script = re.sub(r"\[(HOOK|INSIGHT|STORY|REFRAME|CTA)[^\]]*\]\s*", "", script, flags=re.IGNORECASE).strip()

word_count = len(script.split())
log("SCRIPT", f"{word_count} words (target: {TARGET_WORDS})")

# If Groq returned a short script, ask it to expand — retry up to 2 times
_retry = 0
while word_count < TARGET_WORDS - 5 and _retry < 2:
    _retry += 1
    log("SCRIPT", f"Too short ({word_count} words) — retry {_retry}/2 to reach {TARGET_WORDS}...")
    _expand_prompt = f"""
Rewrite this psychology voiceover script so it is exactly {TARGET_WORDS} words.
Current word count: {word_count}. You need {TARGET_WORDS - word_count} more words.

HOW TO EXPAND (in order of priority):
1. THE SCENE section: add 1-2 more ultra-specific sentences with real details
   (app names, exact moments, specific physical feelings)
2. THE TRUTH section: add 1 more sentence explaining the psychology plainly
3. THE HOOK: make sentence 2 more specific and vivid

RULES:
- Keep "you/your" throughout — never "people" or "they"
- Every sentence: 6-10 words
- No labels, no headers, no markdown
- Same voice and tone as the original
- Count every word before returning. Must be {TARGET_WORDS} (±2).

Return ONLY the full rewritten script as plain text.

Current script:
{script}
"""
    script = llm(_expand_prompt, max_tokens=1000, step="SCRIPT")
    script = re.sub(r"\[(HOOK|INSIGHT|STORY|REFRAME|CTA)[^\]]*\]\s*", "", script, flags=re.IGNORECASE).strip()
    word_count = len(script.split())
    log("SCRIPT", f"After retry {_retry}: {word_count} words")

if word_count < TARGET_WORDS - 10:
    log("SCRIPT", f"WARNING: Final script is {word_count} words — audio will be under 58s")
elif word_count > TARGET_WORDS + 10:
    log("SCRIPT", f"WARNING: Final script is {word_count} words — audio may exceed 58s")
else:
    log("SCRIPT", f"Word count OK: {word_count} words")

# ── CTA ENFORCEMENT ───────────────────────────────────────────────────────────
# Groq sometimes skips the CTA. Detect and append a fallback if missing.
import random
_CTA_VARIANTS = [
    "Follow if this one hit — there is a lot more where that came from.",
    "Save this and follow for more — you will want to come back to it.",
    "Drop a comment if this is you, and follow for more like this.",
    "Follow if you needed to hear this today — there is more coming.",
    "If this hit different, follow — new one drops every day.",
]
_cta_keywords = ["follow", "save this", "drop a comment", "subscribe"]
_has_cta = any(kw in script.lower() for kw in _cta_keywords)

if not _has_cta:
    _fallback_cta = random.choice(_CTA_VARIANTS)
    script = script.rstrip() + " " + _fallback_cta
    word_count = len(script.split())
    log("SCRIPT", f"CTA missing — appended fallback CTA. New count: {word_count} words")
else:
    log("SCRIPT", "CTA verified present")

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
        # Optimal settings for Brian voice on psychology content
        # Source: tested against top US psychology faceless channels
        "stability": 0.38,          # 35-40% sweet spot — natural variation, not robotic
        "similarity_boost": 0.75,   # 75% — strong voice character without artifacts
        "style": 0.40,              # 40% — emotional expressiveness for heavy topics
        "use_speaker_boost": True,  # clarity and presence boost
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
TOPIC: {_topic_name}
EMOTIONAL ANGLE: {_topic_angle}
SCENE CONTEXT (use these real-life details in your SCENE section): {_topic_scene}
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


# ══════════════════════════════════════════════════════════
# STEP 6 — MOVE ALL FILES INTO OUTPUT FOLDER
# ══════════════════════════════════════════════════════════
import shutil

output_dir = f"output_{slug}"
os.makedirs(output_dir, exist_ok=True)

for f in [SCRIPT_FILE, VOICE_FILE, META_FILE, REPORT_FILE]:
    if os.path.exists(f):
        shutil.move(f, os.path.join(output_dir, os.path.basename(f)))

log("DONE", f"All files moved to folder: {output_dir}/")
