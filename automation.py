#!/usr/bin/env python3
import os
import json
import requests
import time
import urllib.parse
import random
import subprocess
from datetime import datetime

GROQ_API            = os.getenv("GROQ_API")
ELEVENLABS_API      = os.getenv("ELEVENLABS_API")
PEXELS_API          = os.getenv("PEXELS_API")

# ── BEST VOICE: Josh — calm, deep, authoritative documentary style ─────────────
ELEVENLABS_VOICE_ID = "TxGEqnHWrfWFTfGW9XjX"
VOICE_FALLBACK_ID   = "pNInz6obpgDQGcFmaJgB"  # Adam fallback

# ── TARGET DURATION: 58 seconds exactly ───────────────────────────────────────
TARGET_DURATION = 58
TARGET_WORDS    = 145  # ~145 words = ~58 seconds at natural pace

# ── Rotating CTAs ──────────────────────────────────────────────────────────────
CTAS = [
    "Follow for more psychology facts that will blow your mind.",
    "Save this. Most people scroll past and never learn this.",
    "Comment mind blown if this surprised you.",
    "Follow now. New psychology fact drops every single day.",
    "Comment below. Have you ever experienced this yourself?",
    "Follow for daily psychology facts most people never learn.",
    "Save this video before you forget it.",
    "Follow. Your mind will thank you later.",
]

# ── Topic categories for viral US psychology content ──────────────────────────
TOPIC_CATEGORIES = [
    {
        "category": "Dark Psychology & Manipulation",
        "examples": [
            "The silent treatment and why it works as emotional control",
            "How narcissists make you feel crazy on purpose",
            "The manipulation tactic your boss uses without you knowing",
            "Why gaslighting makes you doubt your own memory",
        ],
        "visual_style": "dark dramatic lighting, shadowed faces, red and black tones, manipulative expressions",
        "pexels_moods": ["manipulation control", "dark psychology", "person shadow", "emotional abuse", "mind control"]
    },
    {
        "category": "Social Media & Modern Brain",
        "examples": [
            "Why you cannot stop doomscrolling even when you hate it",
            "How Instagram is rewiring your brain like a slot machine",
            "The dark reason likes and comments are addictive as drugs",
            "Why your brain craves notifications at 2am",
        ],
        "visual_style": "cold blue phone light in dark room, ghostly hands from screen, modern digital addiction",
        "pexels_moods": ["phone addiction", "social media night", "person scrolling dark", "digital stress", "screen glow"]
    },
    {
        "category": "Self Sabotage & Subconscious",
        "examples": [
            "Why your brain destroys good things before they happen",
            "The hidden reason you always pick the wrong person",
            "Why you freeze when someone disrespects you",
            "How childhood trauma controls your adult decisions",
        ],
        "visual_style": "split scene calm outside chaotic mind inside, person alone at night overthinking, dramatic shadows",
        "pexels_moods": ["person thinking alone", "overthinking night", "emotional person", "anxiety stress", "alone sad"]
    },
    {
        "category": "Body Language Secrets",
        "examples": [
            "The eye movement that reveals when someone is lying to you",
            "Why crossed arms mean more than just being cold",
            "The fake smile you cannot fake if you know this trick",
            "How to know someone is attracted to you without them saying it",
        ],
        "visual_style": "close up faces with clear emotions, body language details, cinematic realistic people",
        "pexels_moods": ["body language conversation", "face expression close up", "people talking", "emotional interaction", "nonverbal communication"]
    },
    {
        "category": "Cognitive Biases & Decision Making",
        "examples": [
            "Why your brain makes you overpay every single time",
            "The mental trick stores use to empty your wallet",
            "Why you keep choosing the same bad options at restaurants",
            "How your brain was hacked to buy things you never needed",
        ],
        "visual_style": "symbolic brain visuals, person trapped in maze, puppet with strings, cinematic thought bubbles",
        "pexels_moods": ["decision making", "confused person", "shopping psychology", "mental bias", "brain thinking"]
    },
    {
        "category": "Relationship Psychology",
        "examples": [
            "Why you are more attracted to people who ignore you",
            "The attachment style destroying your relationships silently",
            "Why trauma bonding feels like love but destroys you",
            "The psychology behind why breakups hurt worse than rejection",
        ],
        "visual_style": "two people dramatic interaction, emotional close ups, relationship tension, cinematic lighting",
        "pexels_moods": ["couple tension", "relationship stress", "emotional person", "heartbreak", "love psychology"]
    },
]

print("🔑 Checking API keys...")
missing = []
if not GROQ_API:       missing.append("GROQ_API")
if not ELEVENLABS_API: missing.append("ELEVENLABS_API")
if not PEXELS_API:     missing.append("PEXELS_API")
if missing:
    print(f"❌ Missing secrets: {', '.join(missing)}")
    exit(1)
print("✓ All API keys found!")

print("\n🚀 Starting Psychology Shorts pipeline...")
print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"🎯 Target duration: {TARGET_DURATION} seconds")

groq_headers = {
    "Authorization": f"Bearer {GROQ_API}",
    "Content-Type": "application/json"
}

cta = random.choice(CTAS)
category = random.choice(TOPIC_CATEGORIES)
print(f"✓ Category: {category['category']}")
print(f"✓ CTA: {cta}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — Generate Psychology Topic + 3 Visual Concepts
# ══════════════════════════════════════════════════════════════════════════════
print("\n1️⃣  Generating psychology topic + visual concepts...")

try:
    topic_res = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=groq_headers,
        json={
            "model": "llama-3.3-70b-versatile",
            "max_tokens": 1200,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a viral YouTube Shorts psychology content expert "
                        "targeting US audiences aged 18-35. "
                        "You create content like the biggest faceless psychology channels. "
                        "You NEVER use: norepinephrine, cortisol, cognitive, consolidation, "
                        "phenomenon, neuroscience, psychological, dopamine, serotonin, amygdala. "
                        "You speak like a close friend revealing a dark secret. "
                        "Return ONLY raw JSON. No markdown. No code fences. No explanation."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Create a VIRAL psychology YouTube Short for US audience 18-35.\n\n"
                        f"CATEGORY: {category['category']}\n"
                        f"EXAMPLE TOPICS FROM THIS CATEGORY:\n"
                        + "\n".join([f"- {e}" for e in category['examples']]) +
                        f"\n\nVISUAL STYLE FOR THIS CATEGORY: {category['visual_style']}\n\n"
                        "VIRAL RULES:\n"
                        "- Hook = stops scrolling in under 2 seconds\n"
                        "- Fact = feels PERSONAL about THEM specifically\n"
                        "- Connects to: dating, money, work or social media\n"
                        "- Language = 8th grade reading level max\n"
                        "- Title = power words: Secret, Dark, Never, Shocking, Hidden, Why\n\n"
                        "For each of the 3 Pexels searches, think:\n"
                        "- Search 1 = HOOK visual (emotional, shocking, stops scrolling)\n"
                        "- Search 2 = CONCEPT visual (explains the psychology)\n"
                        "- Search 3 = IMPACT visual (why it matters, relatable scene)\n"
                        "- Search 4 = EMOTIONAL close up (face showing the emotion)\n"
                        "- Search 5 = RESOLUTION visual (awareness, realization)\n\n"
                        "Return ONLY this JSON:\n"
                        "{\n"
                        '  "topic": "specific relatable topic max 8 words",\n'
                        '  "niche": "category name",\n'
                        '  "hook": "shocking opener 6-8 words stops scrolling",\n'
                        '  "fact": "2 short punchy sentences no jargon feels personal",\n'
                        '  "why_it_matters": "2 sentences connecting to dating/money/work/social media",\n'
                        '  "real_example": "1 specific American scenario eg at work on a date",\n'
                        '  "pexels_searches": ["hook visual", "concept visual", "impact visual", "emotion closeup", "resolution visual"],\n'
                        '  "title": "YouTube title max 60 chars with power words",\n'
                        '  "description": "YouTube description max 200 chars with hashtags"\n'
                        "}"
                    )
                }
            ]
        },
        timeout=30
    )
    topic_res.raise_for_status()
    raw = topic_res.json()["choices"][0]["message"]["content"].strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"): raw = raw[4:]
    topic = json.loads(raw.strip())
    print(f"✓ Topic: {topic['topic']}")
    print(f"✓ Hook: {topic['hook']}")
    print(f"✓ Searches: {topic['pexels_searches']}")
except Exception as e:
    print(f"❌ Step 1 failed: {e}")
    exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — Write Exactly 58-Second Viral Script
# ══════════════════════════════════════════════════════════════════════════════
print("\n2️⃣  Writing 58-second viral script...")

try:
    script_res = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=groq_headers,
        json={
            "model": "llama-3.3-70b-versatile",
            "max_tokens": 800,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You write the most viral psychology YouTube Shorts in America. "
                        "Channels with millions of views use your scripts. "
                        "Your scripts feel like a trusted friend revealing a dark secret. "
                        "ABSOLUTELY BANNED WORDS: norepinephrine, cortisol, cognitive, "
                        "consolidation, phenomenon, neuroscience, psychological, dopamine, "
                        "serotonin, amygdala, prefrontal, hippocampus, neurological. "
                        "Write in plain conversational American English. "
                        "Every single sentence makes the viewer NEED to hear the next. "
                        "Use dramatic pauses with ... for effect. "
                        "Return ONLY the spoken script text. Nothing else. No labels."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Write a VIRAL psychology YouTube Shorts script.\n\n"
                        f"Topic: {topic['topic']}\n"
                        f"Category: {topic['niche']}\n"
                        f"Hook: {topic['hook']}\n"
                        f"Core fact: {topic['fact']}\n"
                        f"Why it matters: {topic['why_it_matters']}\n"
                        f"Real example: {topic['real_example']}\n"
                        f"End with EXACT CTA: {cta}\n\n"
                        f"SCRIPT STRUCTURE (total {TARGET_WORDS} words = 58 seconds):\n"
                        "1. HOOK (15 words) — first 3 seconds, shock them immediately\n"
                        "2. DARK REVEAL (35 words) — drop the psychology fact like a secret\n"
                        "3. REAL EXAMPLE (30 words) — scene they recognize from their life\n"
                        "4. PERSONAL IMPACT (35 words) — why this affects THEM right now\n"
                        "5. CLIFFHANGER (15 words) — question that makes them comment\n"
                        "6. CTA (15 words) — exact CTA provided above word for word\n\n"
                        "STRICT RULES:\n"
                        "- EXACTLY 140-150 words total (= 58 seconds spoken)\n"
                        "- MAX 8 words per sentence\n"
                        "- Use YOU and YOUR every 2nd sentence\n"
                        "- Zero banned scientific terms\n"
                        "- Use ... for dramatic pauses\n"
                        "- NO hey, welcome, today, hi guys, in this video\n"
                        "- Return ONLY the script text\n\n"
                        "PERFECT EXAMPLE STYLE:\n"
                        "Your brain is hiding something from you.\n"
                        "Right now. Every single day.\n"
                        "Here is the dark truth nobody tells you.\n"
                        "Your mind makes choices... before you even think.\n"
                        "Seven seconds before you decide... it is already done.\n"
                        "Think about that argument you walked away from.\n"
                        "Your brain had already decided the outcome.\n"
                        "Before you even opened your mouth.\n"
                        "This is why you keep repeating the same patterns.\n"
                        "The same relationships. The same jobs. The same mistakes.\n"
                        "You are not broken.\n"
                        "Your past is just running the show.\n"
                        "So right now... who is actually driving your life?\n"
                        "Follow for more psychology facts that will blow your mind."
                    )
                }
            ]
        },
        timeout=30
    )
    script_res.raise_for_status()
    script = script_res.json()["choices"][0]["message"]["content"].strip()
    script = script.strip('"').strip("'")
    word_count = len(script.split())
    print(f"✓ Script: {word_count} words (~{word_count/2.5:.0f} seconds)")
    print(f"✓ Preview: {' '.join(script.split()[:15])}...")
except Exception as e:
    print(f"❌ Step 2 failed: {e}")
    exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — Save Files
# ══════════════════════════════════════════════════════════════════════════════
print("\n3️⃣  Saving files...")

try:
    with open("script.txt", "w", encoding="utf-8") as f:
        f.write(f"TOPIC: {topic['topic']}\n")
        f.write(f"CATEGORY: {topic['niche']}\n")
        f.write(f"HOOK: {topic['hook']}\n")
        f.write(f"CTA: {cta}\n")
        f.write(f"WORD COUNT: {len(script.split())}\n\n")
        f.write("=" * 50 + "\n")
        f.write("VOICEOVER SCRIPT:\n")
        f.write("=" * 50 + "\n\n")
        f.write(script)

    with open("metadata.txt", "w", encoding="utf-8") as f:
        f.write(f"TITLE:\n{topic['title']}\n\n")
        f.write(f"DESCRIPTION:\n{topic['description']}\n\n")
        f.write(f"TOPIC:\n{topic['topic']}\n\n")
        f.write(f"CATEGORY:\n{topic['niche']}\n\n")
        f.write(f"HOOK:\n{topic['hook']}\n\n")
        f.write(f"CTA:\n{cta}\n\n")
        f.write(
            "TAGS:\npsychology, dark psychology, mind tricks, brain facts, "
            "human behavior, mental health, shorts, psychology facts, "
            "mind blowing, self improvement, us psychology\n\n"
        )
        f.write(f"SCRIPT:\n{script}\n")
    print("✓ script.txt saved")
    print("✓ metadata.txt saved")
except Exception as e:
    print(f"❌ Step 3 failed: {e}")
    exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — Generate Voiceover (Josh - calm deep voice)
# ══════════════════════════════════════════════════════════════════════════════
print("\n4️⃣  Generating voiceover...")

def generate_voice(voice_id, script_text):
    res = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={"xi-api-key": ELEVENLABS_API, "Content-Type": "application/json"},
        json={
            "text": script_text,
            "model_id": "eleven_flash_v2_5",
            "voice_settings": {
                "stability": 0.38,
                "similarity_boost": 0.76,
                "style": 0.28,
                "use_speaker_boost": True
            }
        },
        timeout=60
    )
    return res

try:
    print("   Trying Josh voice (calm, deep, authoritative)...")
    el_res = generate_voice(ELEVENLABS_VOICE_ID, script)

    if el_res.status_code != 200:
        print(f"   Josh failed ({el_res.status_code}), trying Adam...")
        el_res = generate_voice(VOICE_FALLBACK_ID, script)
        if el_res.status_code != 200:
            print(f"❌ Both voices failed: {el_res.text}")
            exit(1)
        print("   ✓ Using Adam voice")
    else:
        print("   ✓ Using Josh voice")

    with open("voiceover.mp3", "wb") as f:
        f.write(el_res.content)

    size = os.path.getsize("voiceover.mp3")
    if size < 1000:
        print("❌ Audio file too small")
        exit(1)
    print(f"✓ Voiceover saved ({size:,} bytes)")

except Exception as e:
    print(f"❌ Step 4 failed: {e}")
    exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 5 — Get Actual Audio Duration
# ══════════════════════════════════════════════════════════════════════════════
print("\n5️⃣  Getting audio duration...")

try:
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1', 'voiceover.mp3'],
        capture_output=True, text=True, timeout=10
    )
    audio_duration = float(result.stdout.strip())
    print(f"✓ Actual duration: {audio_duration:.1f}s (target: {TARGET_DURATION}s)")
except Exception:
    audio_duration = float(TARGET_DURATION)
    print(f"⚠️ Using target duration: {audio_duration}s")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 6 — Download 5 Pexels Clips (topic-specific)
# ══════════════════════════════════════════════════════════════════════════════
print("\n6️⃣  Downloading Pexels clips...")

def download_clip(query, filename):
    """Download a portrait Pexels video clip"""
    try:
        # Try portrait first
        for orientation in ["portrait", "landscape"]:
            res = requests.get(
                f"https://api.pexels.com/videos/search"
                f"?query={urllib.parse.quote(query)}"
                f"&per_page=15&orientation={orientation}",
                headers={"Authorization": PEXELS_API},
                timeout=30
            )
            if res.status_code != 200:
                continue
            videos = res.json().get("videos", [])
            if not videos:
                continue

            random.shuffle(videos)
            for video in videos:
                if video.get("duration", 0) < 4:
                    continue
                files = video.get("video_files", [])
                # Prefer HD files
                good = sorted(
                    [f for f in files if f.get("height", 0) >= 540],
                    key=lambda x: x.get("height", 0), reverse=True
                )
                if not good:
                    good = sorted(files, key=lambda x: x.get("height", 0), reverse=True)
                if not good:
                    continue

                r = requests.get(good[0]["link"], timeout=90, stream=True)
                if r.status_code == 200:
                    with open(filename, "wb") as f:
                        for chunk in r.iter_content(8192):
                            f.write(chunk)
                    if os.path.exists(filename) and os.path.getsize(filename) > 50000:
                        return True
    except Exception as e:
        print(f"   ⚠️ '{query}' error: {e}")
    return False

# Topic-specific searches from Step 1 + category fallbacks
searches = topic.get('pexels_searches', category['pexels_moods'])
fallbacks = category['pexels_moods'] + [
    'person thinking', 'brain neurons', 'emotional person',
    'psychology mind', 'stressed person', 'social media night',
    'dark thoughts', 'human behavior'
]

clips = []
for i in range(5):
    fname = f"clip_{i}.mp4"
    query = searches[i] if i < len(searches) else fallbacks[i % len(fallbacks)]
    print(f"   [{i+1}/5] '{query}'...")
    if download_clip(query, fname):
        clips.append(fname)
        print(f"   ✓ Clip {i+1} ready")
    else:
        fb = fallbacks[i % len(fallbacks)]
        print(f"   Fallback: '{fb}'...")
        if download_clip(fb, fname):
            clips.append(fname)
            print(f"   ✓ Clip {i+1} ready (fallback)")
        else:
            print(f"   ⚠️ Clip {i+1} skipped")

print(f"✓ {len(clips)}/5 clips downloaded")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 7 — Process Clips (crop 9:16, resize 720x1280, enhance)
# ══════════════════════════════════════════════════════════════════════════════
print("\n7️⃣  Processing clips...")

processed = []
clip_dur = audio_duration / max(len(clips), 1)

for i, clip in enumerate(clips):
    out = f"proc_{i}.mp4"
    # Crop to 9:16, scale to 720x1280, 30fps, slight contrast boost
    cmd = (
        f'ffmpeg -i {clip} -t {clip_dur + 0.5} '
        f'-vf "crop=ih*9/16:ih,scale=720:1280,setsar=1,fps=30,'
        f'eq=contrast=1.1:brightness=0.02:saturation=1.2" '
        f'-c:v libx264 -preset fast -crf 20 -an {out} -y 2>/dev/null'
    )
    if os.system(cmd) == 0 and os.path.exists(out) and os.path.getsize(out) > 10000:
        processed.append(out)
        print(f"   ✓ Clip {i+1} processed")
    else:
        # Try without enhancement
        cmd2 = (
            f'ffmpeg -i {clip} -t {clip_dur + 0.5} '
            f'-vf "crop=ih*9/16:ih,scale=720:1280,setsar=1,fps=30" '
            f'-c:v libx264 -preset fast -crf 22 -an {out} -y 2>/dev/null'
        )
        if os.system(cmd2) == 0 and os.path.exists(out) and os.path.getsize(out) > 10000:
            processed.append(out)
            print(f"   ✓ Clip {i+1} processed (basic)")
        else:
            print(f"   ⚠️ Clip {i+1} failed")

# Pad to at least 2 clips
while len(processed) < 2 and processed:
    processed.append(processed[0])

# ══════════════════════════════════════════════════════════════════════════════
# STEP 8 — Stitch All Clips + Create Background Video
# ══════════════════════════════════════════════════════════════════════════════
print("\n8️⃣  Stitching clips into background video...")

bg_video = "background.mp4"

if processed:
    with open("clips.txt", "w") as f:
        for p in processed:
            f.write(f"file '{p}'\n")

    # Concatenate and loop to fill full duration
    result = os.system(
        f'ffmpeg -f concat -safe 0 -i clips.txt '
        f'-stream_loop -1 -t {audio_duration + 1} '
        f'-c:v libx264 -preset fast -crf 20 '
        f'{bg_video} -y 2>/dev/null'
    )

    if result != 0 or not os.path.exists(bg_video) or os.path.getsize(bg_video) < 10000:
        # Simple concat without loop
        result2 = os.system(
            f'ffmpeg -f concat -safe 0 -i clips.txt '
            f'-c:v libx264 -preset fast -crf 20 '
            f'{bg_video} -y 2>/dev/null'
        )
        if result2 != 0:
            print("   ⚠️ Stitch failed, using single clip")
            if processed:
                os.system(
                    f'ffmpeg -stream_loop -1 -i {processed[0]} '
                    f'-t {audio_duration + 1} '
                    f'-c:v libx264 -preset fast -crf 20 '
                    f'{bg_video} -y 2>/dev/null'
                )

# PIL fallback if all video fails
if not os.path.exists(bg_video) or os.path.getsize(bg_video) < 10000:
    print("   Generating PIL background fallback...")
    try:
        from PIL import Image, ImageDraw
        random.seed(int(time.time()))
        img = Image.new('RGB', (720, 1280), (8, 4, 25))
        draw = ImageDraw.Draw(img)
        for y in range(1280):
            draw.line([(0,y),(720,y)], fill=(
                int(8+(y/1280)*15),
                int(4+(y/1280)*8),
                int(25+(y/1280)*55)
            ))
        for _ in range(100):
            x, y = random.randint(0,720), random.randint(0,1280)
            r = random.randint(1,10)
            draw.ellipse([x-r,y-r,x+r,y+r],
                fill=(random.randint(60,150), random.randint(20,80), random.randint(180,255)))
        img.save("bg.jpg", quality=95)
        os.system(
            f'ffmpeg -loop 1 -i bg.jpg -t {audio_duration+1} '
            f'-c:v libx264 -tune stillimage -pix_fmt yuv420p '
            f'{bg_video} -y 2>/dev/null'
        )
        print("   ✓ PIL background created")
    except Exception as e:
        print(f"❌ PIL failed: {e}")
        exit(1)

print(f"✓ Background ready ({os.path.getsize(bg_video):,} bytes)")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 9 — Generate Word-by-Word Subtitles (TikTok style)
# ══════════════════════════════════════════════════════════════════════════════
print("\n9️⃣  Generating word-by-word subtitles...")

def srt_time(s):
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = int(s % 60)
    ms = int((s % 1) * 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"

try:
    words = script.split()
    total_words = len(words)
    wps = total_words / audio_duration

    # 3 words per line = word-by-word effect
    chunk_size = 3
    groups = [words[i:i+chunk_size] for i in range(0, len(words), chunk_size)]

    srt = ""
    for i, group in enumerate(groups):
        start = (i * chunk_size) / wps
        end = min(((i + 1) * chunk_size) / wps, audio_duration)
        # Make sure end > start
        if end <= start:
            end = start + 0.3
        text = " ".join(group).upper()
        srt += f"{i+1}\n{srt_time(start)} --> {srt_time(end)}\n{text}\n\n"

    with open("subs.srt", "w", encoding="utf-8") as f:
        f.write(srt)
    print(f"✓ Subtitles ready ({len(groups)} word groups)")

except Exception as e:
    print(f"⚠️ Subtitle error: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 10 — Render Final Video (58 seconds, subtitles, audio)
# ══════════════════════════════════════════════════════════════════════════════
print("\n🔟  Rendering final 58-second video...")

# Bold yellow TikTok-style word-by-word subtitles
sub_style = (
    "FontName=Arial Black,"
    "FontSize=21,"
    "PrimaryColour=&H00FFFF00,"
    "OutlineColour=&H00000000,"
    "BackColour=&H70000000,"
    "Bold=1,"
    "Outline=3,"
    "Shadow=2,"
    "Alignment=2,"
    "MarginV=120"
)

success = False

# Attempt 1: with subtitles
if os.path.exists("subs.srt"):
    print("   Rendering with subtitles...")
    cmd = (
        f'ffmpeg -i {bg_video} -i voiceover.mp3 '
        f'-c:v libx264 -c:a aac -b:a 192k '
        f"-vf \"scale=720:1280,subtitles=subs.srt:force_style='{sub_style}'\" "
        f'-pix_fmt yuv420p -t {audio_duration} short.mp4 -y 2>/dev/null'
    )
    result = os.system(cmd)
    if result == 0 and os.path.exists("short.mp4") and os.path.getsize("short.mp4") > 10000:
        success = True
        print("✓ Video with subtitles created!")

# Attempt 2: without subtitles
if not success:
    print("   Rendering without subtitles...")
    cmd2 = (
        f'ffmpeg -i {bg_video} -i voiceover.mp3 '
        f'-c:v libx264 -c:a aac -b:a 192k '
        f'-vf "scale=720:1280" '
        f'-pix_fmt yuv420p -t {audio_duration} short.mp4 -y 2>/dev/null'
    )
    result2 = os.system(cmd2)
    if result2 == 0 and os.path.exists("short.mp4") and os.path.getsize("short.mp4") > 10000:
        success = True
        print("✓ Video created (no subtitles)")

if not success:
    print("❌ Video creation failed completely")
    exit(1)

# ── Final Stats ────────────────────────────────────────────────────────────────
size = os.path.getsize("short.mp4")

# Get final video duration
try:
    dur_result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1', 'short.mp4'],
        capture_output=True, text=True, timeout=10
    )
    final_dur = float(dur_result.stdout.strip())
except Exception:
    final_dur = audio_duration

print(f"\n{'='*50}")
print(f"✅ ALL DONE! Psychology Short Created! 🎉")
print(f"{'='*50}")
print(f"📹 Title:    {topic['title']}")
print(f"🎯 Category: {topic['niche']}")
print(f"⏱️  Duration: {final_dur:.1f} seconds")
print(f"📦 Size:     {size/1024/1024:.1f} MB")
print(f"{'='*50}")
print(f"\n📄 Output files:")
print(f"   short.mp4     → Upload to YouTube Shorts")
print(f"   voiceover.mp3 → Audio only backup")
print(f"   script.txt    → Full script + CTA")
print(f"   metadata.txt  → Title, description, tags")
print(f"   subs.srt      → Subtitle file")
