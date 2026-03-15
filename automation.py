import os
import re
import sys
import json
import random
import shutil
import requests
import subprocess
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional, Tuple

# ══════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════

GROQ_API       = os.getenv("GROQ_API")
CLAUDE_API     = os.getenv("CLAUDE_API")
ELEVENLABS_API = os.getenv("ELEVENLABS_API")
PEXELS_API     = os.getenv("PEXELS_API")

USE_TRENDS     = os.getenv("USE_TRENDS", "1") == "1"

# ── VOICE SELECTION ───────────────────────────────────────────────────────────
# US Healthcare News & Explainers niche requires:
# clear, trustworthy, calm American delivery.
# The voice should sound like a smart explainer, not a dramatic narrator.
# Best tone: simple, reassuring, useful, direct.
VOICE_ID = "nPczCjzI2devNBz1zQrb"   # Brian
ELEVENLABS_MODEL = "eleven_turbo_v2_5"

TARGET_WORDS = 150
TITLE_MIN = 40
TITLE_MAX = 58
MIN_AUDIO_FILESIZE = 10_000

# ══════════════════════════════════════════════════════════
# LOGGING
# ══════════════════════════════════════════════════════════

def log(step: str, msg: str = ""):
    print(f"[{step}] {msg}" if msg else f"[{step}]", flush=True)

# ══════════════════════════════════════════════════════════
# STARTUP VALIDATION
# ══════════════════════════════════════════════════════════

missing = []
if not GROQ_API:
    missing.append("GROQ_API")
if not ELEVENLABS_API:
    missing.append("ELEVENLABS_API")

if missing:
    log("ERROR", "Missing required GitHub secrets:")
    for m in missing:
        log("ERROR", f"  • {m}")
    sys.exit(1)

log("CONFIG", f"Voice: {VOICE_ID} | Model: {ELEVENLABS_MODEL} | Target: {TARGET_WORDS} words")
log("CONFIG", f"Use Trends: {USE_TRENDS} | Claude fallback: {'yes' if CLAUDE_API else 'no'} | Pexels: {'yes' if PEXELS_API else 'no'}")

# ══════════════════════════════════════════════════════════
# LLM LAYER — Groq primary, Claude fallback
# ══════════════════════════════════════════════════════════

def _groq(prompt: str, max_tokens: int, temperature: float = 0.8) -> str:
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=75,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()

def _claude(prompt: str, max_tokens: int, temperature: float = 0.8) -> str:
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
        timeout=75,
    )
    if not r.ok:
        raise RuntimeError(f"Claude {r.status_code}: {r.text[:200]}")
    return r.json()["content"][0]["text"].strip()

def llm(prompt: str, max_tokens: int = 1000, step: str = "", temperature: float = 0.8) -> str:
    try:
        return _groq(prompt, max_tokens=max_tokens, temperature=temperature)
    except Exception as e:
        log(step or "LLM", f"Groq failed: {e}")
        if CLAUDE_API:
            log(step or "LLM", "Retrying with Claude...")
            try:
                return _claude(prompt, max_tokens=max_tokens, temperature=temperature)
            except Exception as e2:
                raise RuntimeError(f"Both LLMs failed. Last error: {e2}") from e2
        raise RuntimeError(f"Groq failed and no fallback set: {e}") from e

# ══════════════════════════════════════════════════════════
# UTILITIES
# ══════════════════════════════════════════════════════════

def count_words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))

def clean_slug(text: str) -> str:
    s = text.lower()
    s = re.sub(r"[‘’'`]", "", s)
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")[:60]

def strip_labels(text: str) -> str:
    return re.sub(
        r"\[(HOOK|EXPLANATION|IMPACT|TAKEAWAY|CTA|TITLE|DESCRIPTION|HASHTAGS|TAGS|THUMBNAIL|SCENE|VISUAL)[^\]]*\]\s*",
        "",
        text,
        flags=re.IGNORECASE
    ).strip()

def safe_json_loads(raw: str) -> Optional[dict]:
    raw = raw.strip()
    try:
        return json.loads(raw)
    except Exception:
        match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                return None
    return None

def save_text(path: str, text: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def health_safety_clean(text: str) -> str:
    replacements = [
        (r"\bcure(s|d)?\b", "help manage"),
        (r"\bguarantee(d)?\b", "may help"),
        (r"\byou definitely have\b", "it may be a sign"),
        (r"\bthis means you have\b", "this can sometimes point to"),
        (r"\bwill prevent\b", "may help lower the risk of"),
        (r"\b100%\b", "strongly"),
    ]
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
    return text.strip()

# ══════════════════════════════════════════════════════════
# EVERGREEN TOPICS
# ══════════════════════════════════════════════════════════

EVERGREEN_TOPICS = [
    ("high blood pressure warning signs",
     "common signs Americans ignore before blood pressure becomes dangerous",
     "headaches, dizziness, blurred vision, home blood pressure cuffs, pharmacy readings",
     "warning"),

    ("prediabetes signs",
     "small symptoms people dismiss before diabetes gets worse",
     "constant thirst, fatigue, frequent urination, late-night snacking, blood sugar tests",
     "symptom"),

    ("ultra-processed foods",
     "why everyday packaged foods may be hurting long-term health",
     "breakfast cereals, frozen meals, soda, chips, ingredient labels, grocery carts",
     "habit"),

    ("walking for heart health",
     "what walking daily actually does for your body",
     "30-minute walks, smartwatch step counts, neighborhood sidewalks, after-dinner walks",
     "habit"),

    ("sleep and blood sugar",
     "how bad sleep quietly affects hunger, weight, and blood sugar",
     "scrolling at midnight, short sleep, morning cravings, energy crashes, coffee dependence",
     "habit"),

    ("dehydration symptoms",
     "how your body warns you before dehydration gets serious",
     "dry mouth, dark urine, headaches, summer heat, gym sessions, water bottles",
     "symptom"),

    ("health insurance deductibles",
     "why many Americans think insurance covers more than it actually does",
     "doctor visits, surprise bills, deductibles, copays, out-of-pocket costs",
     "cost"),

    ("ER vs urgent care",
     "when Americans should choose urgent care instead of the emergency room",
     "fever, sprains, chest pain, waiting rooms, medical bills, late-night symptoms",
     "cost"),

    ("cholesterol explained simply",
     "what good and bad cholesterol actually mean in real life",
     "lab results, annual checkups, fried food, family history, prescription statins",
     "myth"),

    ("stroke warning signs",
     "the early signs of stroke Americans should never ignore",
     "face drooping, arm weakness, slurred speech, calling 911, FAST warning signs",
     "warning"),

    ("heart attack symptoms",
     "how heart attack symptoms can look different than people expect",
     "chest pressure, jaw pain, nausea, sweating, shortness of breath",
     "warning"),

    ("sodium and blood pressure",
     "why too much sodium affects more than just salty food cravings",
     "fast food, canned soup, frozen dinners, restaurant meals, nutrition labels",
     "habit"),

    ("how to read nutrition labels",
     "the part of food labels most shoppers never notice",
     "serving size, added sugar, sodium, protein claims, grocery shopping",
     "myth"),

    ("medical debt in America",
     "why one hospital visit can turn into long-term financial stress",
     "ambulance bills, insurance gaps, payment plans, collections, emergency care",
     "cost"),

    ("why Americans feel tired all the time",
     "the everyday health habits behind constant fatigue",
     "poor sleep, dehydration, blood sugar spikes, stress, low movement, screen time",
     "symptom"),
]

HEALTH_KEYWORDS = [
    "health", "medical", "medicine", "hospital", "doctor", "nurse", "symptoms",
    "blood pressure", "diabetes", "heart", "stroke", "cholesterol", "sleep",
    "fatigue", "hydration", "dehydration", "nutrition", "insurance", "deductible",
    "urgent care", "emergency room", "prescription", "flu", "covid", "virus",
    "sodium", "sugar", "food", "walking", "weight", "tired", "wellness"
]

# ══════════════════════════════════════════════════════════
# TRENDS — FREE SIMPLE INGESTION
# ══════════════════════════════════════════════════════════

def is_health_related(text: str) -> bool:
    t = text.lower()
    return any(k in t for k in HEALTH_KEYWORDS)

def fetch_google_trends_rss_us() -> List[str]:
    if not USE_TRENDS:
        return []
    url = "https://trends.google.com/trending/rss?geo=US"
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        root = ET.fromstring(r.text)
        items = []
        for item in root.findall(".//item"):
            title = item.findtext("title", default="").strip()
            if title:
                items.append(title)
        return items
    except Exception as e:
        log("TRENDS", f"Google Trends fetch failed: {e}")
        return []

def choose_evergreen_topic() -> Dict:
    counter_file = "topic_counter.txt"
    try:
        with open(counter_file, "r") as f:
            run_count = int(f.read().strip())
    except (FileNotFoundError, ValueError):
        run_count = 0

    run_count += 1
    idx = (run_count - 1) % len(EVERGREEN_TOPICS)

    with open(counter_file, "w") as f:
        f.write(str(run_count))

    t = EVERGREEN_TOPICS[idx]
    return {
        "topic_name": t[0],
        "angle": t[1],
        "scene_context": t[2],
        "hook_type": t[3],
        "source": "evergreen",
        "source_item": "evergreen_rotation"
    }

def build_topic_from_trend(raw_item: str) -> Optional[Dict]:
    prompt = f"""
Convert this US trend into a healthcare YouTube Shorts topic only if it can be turned into
a useful, practical health explainer for Americans.

RAW ITEM:
{raw_item}

Return ONLY valid JSON:
{{
  "usable": true,
  "topic_name": "...",
  "angle": "...",
  "scene_context": "...",
  "hook_type": "symptom|warning|myth|cost|habit|news"
}}

RULES:
- if the trend is not useful for a health explainer, return usable=false
- topic_name must be short and searchable
- angle must explain why it matters
- scene_context must contain concrete real-life details
- no fake medical claims
"""
    raw = llm(prompt, max_tokens=220, step="TREND", temperature=0.55)
    data = safe_json_loads(raw)
    if not data:
        return None
    if not data.get("usable"):
        return None
    if not all(k in data for k in ["topic_name", "angle", "scene_context", "hook_type"]):
        return None

    data["source"] = "trend"
    data["source_item"] = raw_item
    return data

def select_topic() -> Tuple[Dict, List[str]]:
    trend_items = fetch_google_trends_rss_us()
    log("TRENDS", f"Fetched {len(trend_items)} Google Trends items")

    health_candidates = [x for x in trend_items if is_health_related(x)]
    log("TRENDS", f"Health-filtered trend items: {len(health_candidates)}")

    random.shuffle(health_candidates)
    considered = []

    for item in health_candidates[:5]:
        considered.append(item)
        built = build_topic_from_trend(item)
        if built:
            log("TOPIC", f"Using trend topic: {built['topic_name']}")
            return built, considered

    fallback = choose_evergreen_topic()
    log("TOPIC", f"Using evergreen fallback: {fallback['topic_name']}")
    return fallback, considered

selected_topic, considered_trends = select_topic()

_topic_name = selected_topic["topic_name"]
_topic_angle = selected_topic["angle"]
_topic_scene = selected_topic["scene_context"]
_topic_hook_type = selected_topic["hook_type"]
topic_source = selected_topic["source"]

# ══════════════════════════════════════════════════════════
# STEP 1 — COMPACT CONTENT PACK
# title + alt titles + thumbnail hook + cta + script
# ══════════════════════════════════════════════════════════

log("CONTENT", "Generating title + alt titles + script + thumbnail hook...")

CONTENT_PACK_PROMPT = f"""
You are creating a complete content pack for a US healthcare YouTube Shorts channel.

TOPIC: {_topic_name}
ANGLE: {_topic_angle}
SCENE CONTEXT: {_topic_scene}
HOOK TYPE: {_topic_hook_type}
SOURCE: {topic_source}

AUDIENCE:
Americans 18-44 who care about health symptoms, nutrition, prevention,
sleep, heart health, diabetes, blood pressure, insurance, and medical costs.

GOAL:
Generate a high-retention, trustworthy, highly clickable YouTube Shorts content pack.

Return ONLY valid JSON in this exact format:
{{
  "title": "...",
  "alt_titles": ["...", "..."],
  "thumbnail_hook": "...",
  "cta": "...",
  "script": "..."
}}

HOOK PRIORITY:
- the first sentence of the script must stop the scroll
- strongest health hooks are:
  1. warning signs people ignore
  2. common mistakes Americans make
  3. body signals that mean more than people think
  4. medical cost misunderstandings
  5. food or sleep habits with hidden effects

RULES FOR TITLE:
- {TITLE_MIN}-{TITLE_MAX} characters
- plain American English
- no ALL CAPS
- no exclamation marks
- useful, urgent, believable
- strong health curiosity
- not spammy

RULES FOR ALT TITLES:
- exactly 2 alternates
- same quality level as the main title
- different wording, same topic

RULES FOR THUMBNAIL HOOK:
- 3 to 6 words
- easy to read fast
- strong curiosity
- no punctuation if possible

RULES FOR CTA:
- natural and non-salesy
- use follow, save, share, or comment

RULES FOR SCRIPT:
- exactly {TARGET_WORDS} words
- 55 to 60 second spoken flow
- plain American English
- clear, useful, calm, direct
- 6th to 8th grade reading level
- no diagnosing
- no prescribing medication
- no fearmongering
- no overpromising
- do not use these openers:
  "Have you ever"
  "Did you know"
  "In this video"
  "Today we're talking about"

SCRIPT STRUCTURE:
1. Hook — 3 sentences
2. Explanation — 4 sentences
3. Real-life impact — 4 sentences
4. Takeaway — 3 sentences
5. CTA — 1 sentence

If symptoms are serious or urgent, say to seek medical care.

Return JSON only.
"""

content_raw = llm(CONTENT_PACK_PROMPT, max_tokens=1400, step="CONTENT", temperature=0.78)
content_data = safe_json_loads(content_raw)

if not content_data:
    log("CONTENT", "JSON parse failed — retrying with stricter repair prompt...")
    repair_prompt = f"""
Fix this into valid JSON only.

RAW:
{content_raw}

Required format:
{{
  "title": "...",
  "alt_titles": ["...", "..."],
  "thumbnail_hook": "...",
  "cta": "...",
  "script": "..."
}}
"""
    content_raw = llm(repair_prompt, max_tokens=1400, step="CONTENT", temperature=0.3)
    content_data = safe_json_loads(content_raw)

if not content_data:
    log("ERROR", "Could not parse content pack JSON")
    sys.exit(1)

title = str(content_data.get("title", "")).strip().strip('"\'').strip(".")
alt_titles = content_data.get("alt_titles", [])
thumbnail_hook = str(content_data.get("thumbnail_hook", "")).strip()
cta = str(content_data.get("cta", "")).strip()
script = str(content_data.get("script", "")).strip()

script = strip_labels(script)
script = health_safety_clean(script)

if len(title) < TITLE_MIN or len(title) > TITLE_MAX:
    log("TITLE", f"Repairing title length ({len(title)})")
    repair_title_prompt = f"""
Rewrite this title so it is between {TITLE_MIN} and {TITLE_MAX} characters.

TITLE:
{title}

Keep it health-focused, clickable, useful, and trustworthy.
Return ONLY the final title.
"""
    title = llm(repair_title_prompt, max_tokens=70, step="TITLE", temperature=0.45).strip().strip('"\'').strip(".")

if not isinstance(alt_titles, list):
    alt_titles = []
alt_titles = [str(x).strip().strip('"\'').strip(".") for x in alt_titles[:2] if str(x).strip()]

CTA_VARIANTS = [
    "Follow for simple health explainers like this.",
    "Save this so you remember it later.",
    "Follow for more health news in plain English.",
    "Share this with someone who needs it.",
    "Follow if you want health facts without the jargon.",
]
CTA_KEYWORDS = ["follow", "save", "share", "comment"]

if not cta or not any(k in cta.lower() for k in CTA_KEYWORDS):
    cta = random.choice(CTA_VARIANTS)

if not any(k in script.lower() for k in CTA_KEYWORDS):
    script = script.rstrip() + " " + cta

word_count = count_words(script)
log("SCRIPT", f"Initial word count: {word_count}")

if word_count < TARGET_WORDS - 3 or word_count > TARGET_WORDS + 3:
    log("SCRIPT", "Repairing script word count...")
    repair_script_prompt = f"""
Rewrite this healthcare YouTube Shorts script so it is exactly {TARGET_WORDS} words.

CURRENT SCRIPT:
{script}

RULES:
- exact word count: {TARGET_WORDS}
- plain American English
- strong first 2 sentences
- trustworthy and useful
- no diagnosis
- no fearbait
- natural spoken pacing
- keep the same topic and CTA style

Return ONLY the rewritten script.
"""
    script = llm(repair_script_prompt, max_tokens=1200, step="SCRIPT", temperature=0.55)
    script = strip_labels(script)
    script = health_safety_clean(script)

if not any(k in script.lower() for k in CTA_KEYWORDS):
    script = script.rstrip() + " " + cta

word_count = count_words(script)
log("SCRIPT", f"Final word count: {word_count}")

if not thumbnail_hook or len(thumbnail_hook.split()) > 7:
    thumbnail_hook = "Signs people miss"

slug = clean_slug(title)

SCRIPT_FILE = f"{slug}_script.txt"
VOICE_FILE = f"{slug}_voice.mp3"
META_FILE = f"{slug}_metadata.txt"
VISUAL_FILE = f"{slug}_visuals.txt"
VIDEO_PROMPT_FILE = f"{slug}_video_prompts.txt"
REPORT_FILE = f"{slug}_report.txt"
DEBUG_FILE = f"{slug}_debug.json"

with open(SCRIPT_FILE, "w", encoding="utf-8") as f:
    f.write(f"TITLE: {title}\n")
    f.write(f"ALT TITLES: {', '.join(alt_titles) if alt_titles else 'N/A'}\n")
    f.write(f"TOPIC: {_topic_name}\n")
    f.write(f"ANGLE: {_topic_angle}\n")
    f.write(f"SOURCE: {topic_source}\n")
    f.write(f"HOOK TYPE: {_topic_hook_type}\n")
    f.write(f"THUMBNAIL HOOK: {thumbnail_hook}\n")
    f.write(f"WORD COUNT: {word_count}\n")
    f.write("─" * 50 + "\n\n")
    f.write(script)

log("SCRIPT", f"{SCRIPT_FILE} saved")

# ══════════════════════════════════════════════════════════
# STEP 2 — METADATA + VISUAL PACK
# description + hashtags + tags + upload time + 5 scenes
# ══════════════════════════════════════════════════════════

log("PACK", "Generating metadata + visuals pack...")

PACK_PROMPT = f"""
Create a metadata and visuals pack for this US healthcare YouTube Shorts video.

TITLE: {title}
ALT TITLES: {alt_titles}
THUMBNAIL HOOK: {thumbnail_hook}
TOPIC: {_topic_name}
ANGLE: {_topic_angle}
SCENE CONTEXT: {_topic_scene}
HOOK TYPE: {_topic_hook_type}
SCRIPT: {script}

Return ONLY valid JSON in this exact format:
{{
  "description": "...",
  "hashtags": ["...", "...", "..."],
  "tags": ["...", "...", "..."],
  "suggested_upload_time": "...",
  "scene_plan": [
    {{
      "scene": 1,
      "voice_part": "...",
      "visual_idea": "...",
      "caption_overlay": "...",
      "pexels_keywords": ["...", "...", "..."]
    }}
  ]
}}

RULES:
- description must be 2 short sentences under 190 characters total
- sentence 2 must be: Follow for more simple health explainers.
- hashtags: exactly 15
- tags: exactly 25
- scene_plan: exactly 5 scenes
- each caption_overlay must be short, punchy, and readable on Shorts
- each pexels_keywords list must contain exactly 3 search phrases
- visuals should be realistic stock-footage friendly
- use plain American English
- do not use fake medical claims

Scene plan structure:
1. Hook
2. Explanation
3. Real-life impact
4. Takeaway
5. CTA / closing
"""

pack_raw = llm(PACK_PROMPT, max_tokens=1500, step="PACK", temperature=0.7)
pack_data = safe_json_loads(pack_raw)

if not pack_data:
    log("PACK", "JSON parse failed — retrying repair...")
    repair_pack_prompt = f"""
Fix this into valid JSON only.

RAW:
{pack_raw}

Required format:
{{
  "description": "...",
  "hashtags": ["..."],
  "tags": ["..."],
  "suggested_upload_time": "...",
  "scene_plan": [{{}}]
}}
"""
    pack_raw = llm(repair_pack_prompt, max_tokens=1500, step="PACK", temperature=0.3)
    pack_data = safe_json_loads(pack_raw)

if not pack_data:
    log("ERROR", "Could not parse metadata/visual pack JSON")
    sys.exit(1)

description = str(pack_data.get("description", "")).strip()
hashtags = pack_data.get("hashtags", [])
tags = pack_data.get("tags", [])
suggested_upload_time = str(pack_data.get("suggested_upload_time", "Weekdays 6:00 PM ET")).strip()
scene_plan = pack_data.get("scene_plan", [])

if not isinstance(hashtags, list):
    hashtags = []
if not isinstance(tags, list):
    tags = []
if not isinstance(scene_plan, list):
    scene_plan = []

hashtags = [str(x).strip() for x in hashtags[:15] if str(x).strip()]
tags = [str(x).strip() for x in tags[:25] if str(x).strip()]

while len(hashtags) < 15:
    filler = [
        "#health", "#healthnews", "#wellness", "#healthtips", "#prevention",
        "#bloodpressure", "#nutrition", "#diabetes", "#hearthealth", "#symptoms",
        "#sleephealth", "#medicalnews", "#healthcare", "#healthyhabits", "#explainer"
    ]
    for h in filler:
        if h not in hashtags:
            hashtags.append(h)
        if len(hashtags) == 15:
            break

while len(tags) < 25:
    filler_tags = [
        "health news", "simple health explainers", "warning signs", "health facts",
        "blood pressure symptoms", "prediabetes signs", "nutrition tips",
        "heart health", "sleep and health", "healthcare explained",
        "us healthcare", "medical costs", "preventive health", "symptoms explained",
        "healthy habits", "health shorts", "youtube shorts health", "medical myths",
        "warning symptoms", "daily health tips", "american health topics",
        "health education", "plain english health", "stock footage health", "wellness facts"
    ]
    for t in filler_tags:
        if t not in tags:
            tags.append(t)
        if len(tags) == 25:
            break

meta_text = f"""TITLE:
{title}

ALT TITLES:
{alt_titles[0] if len(alt_titles) > 0 else "N/A"}
{alt_titles[1] if len(alt_titles) > 1 else "N/A"}

DESCRIPTION:
{description}

HASHTAGS:
{" ".join(hashtags)}

TAGS:
{", ".join(tags)}

SUGGESTED UPLOAD TIME:
{suggested_upload_time}

THUMBNAIL HOOK:
{thumbnail_hook}
"""
save_text(META_FILE, meta_text)
log("META", f"{META_FILE} saved")

visual_lines = []
visual_lines.append(f"TITLE: {title}")
visual_lines.append(f"THUMBNAIL HOOK: {thumbnail_hook}")
visual_lines.append("")
visual_lines.append("SCENE PLAN:")

for scene in scene_plan[:5]:
    num = scene.get("scene", "?")
    voice_part = scene.get("voice_part", "")
    visual_idea = scene.get("visual_idea", "")
    caption_overlay = scene.get("caption_overlay", "")
    pexels_keywords = scene.get("pexels_keywords", [])

    visual_lines.append(f"\nScene {num}")
    visual_lines.append(f"Voice Part: {voice_part}")
    visual_lines.append(f"Visual Idea: {visual_idea}")
    visual_lines.append(f"Caption Overlay: {caption_overlay}")
    visual_lines.append(f"Pexels Keywords: {', '.join(pexels_keywords)}")

save_text(VISUAL_FILE, "\n".join(visual_lines))
log("VISUALS", f"{VISUAL_FILE} saved")

# ══════════════════════════════════════════════════════════
# STEP 2B — VIDEO PRODUCTION PROMPTS
# scene-by-scene prompts for AI video tools / editors
# ══════════════════════════════════════════════════════════

video_prompt_lines = []
video_prompt_lines.append(f"TITLE: {title}")
video_prompt_lines.append(f"TOPIC: {_topic_name}")
video_prompt_lines.append(f"THUMBNAIL HOOK: {thumbnail_hook}")
video_prompt_lines.append("")
video_prompt_lines.append("AI VIDEO PRODUCTION GUIDE")
video_prompt_lines.append("")

for scene in scene_plan[:5]:
    num = scene.get("scene", "?")
    voice_part = scene.get("voice_part", "")
    visual_idea = scene.get("visual_idea", "")
    caption_overlay = scene.get("caption_overlay", "")
    pexels_keywords = scene.get("pexels_keywords", [])

    video_prompt_lines.append(f"Scene {num}")
    video_prompt_lines.append(f"Voice Purpose: {voice_part}")
    video_prompt_lines.append(f"Best Visual Direction: {visual_idea}")
    video_prompt_lines.append(
        f"AI Video Prompt: Realistic vertical 9:16 healthcare explainer scene showing {visual_idea.lower()}, modern American setting, natural lighting, cinematic but realistic, subtle camera motion, highly detailed, clean composition"
    )
    video_prompt_lines.append(f"Stock Footage Prompt: {', '.join(pexels_keywords)}")
    video_prompt_lines.append(f"On-Screen Text: {caption_overlay}")
    video_prompt_lines.append("Edit Style: Fast Shorts pacing, bold readable captions, subtle zoom-ins, quick clean cuts, mobile-first framing")
    video_prompt_lines.append("")

save_text(VIDEO_PROMPT_FILE, "\n".join(video_prompt_lines))
log("VIDEO", f"{VIDEO_PROMPT_FILE} saved")

# ══════════════════════════════════════════════════════════
# STEP 3 — OPTIONAL PEXELS LOOKUP
# ══════════════════════════════════════════════════════════

pexels_results = []

def pexels_search(query: str, per_page: int = 3) -> List[Dict]:
    if not PEXELS_API:
        return []
    try:
        r = requests.get(
            "https://api.pexels.com/videos/search",
            headers={"Authorization": PEXELS_API},
            params={"query": query, "per_page": per_page},
            timeout=30,
        )
        r.raise_for_status()
        return r.json().get("videos", [])
    except Exception as e:
        log("PEXELS", f"Search failed for '{query}': {e}")
        return []

if PEXELS_API and scene_plan:
    log("PEXELS", "Searching stock footage ideas...")
    for scene in scene_plan[:5]:
        keywords = scene.get("pexels_keywords", [])
        if keywords:
            query = keywords[0]
            results = pexels_search(query, per_page=2)
            pexels_results.append({
                "scene": scene.get("scene"),
                "query": query,
                "results_found": len(results),
                "video_urls": [v.get("url") for v in results[:2] if v.get("url")]
            })

# ══════════════════════════════════════════════════════════
# STEP 4 — VOICE
# ══════════════════════════════════════════════════════════

log("VOICE", "Generating audio...")

voice_payload = {
    "text": script,
    "model_id": ELEVENLABS_MODEL,
    "voice_settings": {
        "stability": 0.45,
        "similarity_boost": 0.78,
        "style": 0.22,
        "use_speaker_boost": True,
    },
}

voice_res = requests.post(
    f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
    headers={
        "xi-api-key": ELEVENLABS_API,
        "Content-Type": "application/json"
    },
    json=voice_payload,
    timeout=90,
)

if not voice_res.ok:
    log("ERROR", f"ElevenLabs {voice_res.status_code}: {voice_res.text[:300]}")
    sys.exit(1)

with open(VOICE_FILE, "wb") as f:
    f.write(voice_res.content)

if os.path.getsize(VOICE_FILE) < MIN_AUDIO_FILESIZE:
    log("ERROR", f"{VOICE_FILE} is suspiciously small")
    sys.exit(1)

probe = subprocess.run(
    [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        VOICE_FILE
    ],
    capture_output=True,
    text=True,
)

try:
    actual_duration = float(probe.stdout.strip())
    log("VOICE", f"{VOICE_FILE} saved — {actual_duration:.1f}s | {os.path.getsize(VOICE_FILE)//1024}KB")
except Exception:
    actual_duration = None
    log("VOICE", f"{VOICE_FILE} saved — duration unknown")

# ══════════════════════════════════════════════════════════
# STEP 5 — DEBUG + REPORT
# ══════════════════════════════════════════════════════════

debug_payload = {
    "selected_topic": selected_topic,
    "considered_trends": considered_trends,
    "title": title,
    "alt_titles": alt_titles,
    "thumbnail_hook": thumbnail_hook,
    "cta": cta,
    "word_count": word_count,
    "audio_duration": actual_duration,
    "scene_plan": scene_plan,
    "pexels_results": pexels_results,
}

save_text(DEBUG_FILE, json.dumps(debug_payload, indent=2))
log("DEBUG", f"{DEBUG_FILE} saved")

duration_str = f"{actual_duration:.1f}s" if actual_duration else "unknown"

report = f"""
╔══════════════════════════════════════════════════════╗
║   FREE-TIER HEALTHCARE SHORTS — RUN REPORT          ║
╚══════════════════════════════════════════════════════╝

TITLE:        {title}
ALT TITLES:   {alt_titles}
TOPIC:        {_topic_name}
ANGLE:        {_topic_angle}
SOURCE:       {topic_source}
HOOK TYPE:    {_topic_hook_type}
WORD COUNT:   {word_count} words  (target: {TARGET_WORDS})
AUDIO:        {duration_str}
VOICE ID:     {VOICE_ID}
MODEL:        {ELEVENLABS_MODEL}

THUMBNAIL HOOK:
  {thumbnail_hook}

SUGGESTED UPLOAD TIME:
  {suggested_upload_time}

OUTPUT FILES:
  {SCRIPT_FILE}
  {VOICE_FILE}
  {META_FILE}
  {VISUAL_FILE}
  {VIDEO_PROMPT_FILE}
  {REPORT_FILE}
  {DEBUG_FILE}

SCRIPT PREVIEW:
{". ".join(script.split(". ")[:3])}.
""".strip()

save_text(REPORT_FILE, report)
print("\n" + report + "\n")
log("DONE", f"All files ready: {SCRIPT_FILE} | {VOICE_FILE} | {META_FILE} | {VISUAL_FILE} | {VIDEO_PROMPT_FILE} | {REPORT_FILE} | {DEBUG_FILE}")

# ══════════════════════════════════════════════════════════
# STEP 6 — MOVE TO OUTPUT FOLDER
# ══════════════════════════════════════════════════════════

output_dir = f"output_{slug}"
os.makedirs(output_dir, exist_ok=True)

for f in [SCRIPT_FILE, VOICE_FILE, META_FILE, VISUAL_FILE, VIDEO_PROMPT_FILE, REPORT_FILE, DEBUG_FILE]:
    if os.path.exists(f):
        shutil.move(f, os.path.join(output_dir, os.path.basename(f)))

log("DONE", f"All files moved to folder: {output_dir}/")
