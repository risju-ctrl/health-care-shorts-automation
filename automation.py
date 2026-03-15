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

# ── BEST VOICE: Josh — calm, deep, authoritative ──────────────────────────────
# Used by top documentary & psychology YouTube channels
ELEVENLABS_VOICE_ID = "TxGEqnHWrfWFTfGW9XjX"

CTAS = [
    "Follow for more psychology facts that will blow your mind.",
    "Save this video. You will want to watch it again.",
    "Comment below. Did this change how you see yourself?",
    "Follow now. New psychology fact drops every single day.",
    "Save this. Most people scroll past and never learn this.",
    "Comment mind blown if this surprised you.",
    "Follow for daily psychology facts most people never learn.",
    "Save this video before you forget it.",
    "Comment below. Have you ever experienced this yourself?",
    "Follow. Your mind will thank you later.",
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

groq_headers = {
    "Authorization": f"Bearer {GROQ_API}",
    "Content-Type": "application/json"
}

cta = random.choice(CTAS)
print(f"✓ CTA: {cta}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — Generate Psychology Topic
# ══════════════════════════════════════════════════════════════════════════════
print("\n1️⃣  Generating psychology topic...")

try:
    topic_res = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=groq_headers,
        json={
            "model": "llama-3.3-70b-versatile",
            "max_tokens": 800,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a viral YouTube Shorts psychology content expert "
                        "with 10 million US subscribers aged 18-35. "
                        "You write like a friend texting a shocking secret. "
                        "NEVER use: norepinephrine, cortisol, cognitive, consolidation, phenomenon. "
                        "Return ONLY raw JSON. No markdown. No code fences. No explanation."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        "Create a VIRAL psychology YouTube Shorts topic for US audience 18-35.\n\n"
                        "RANDOMLY PICK ONE NICHE:\n"
                        "- Dark psychology tricks people use on you every day\n"
                        "- Shocking things your brain does behind your back\n"
                        "- Why you keep sabotaging yourself without knowing\n"
                        "- Hidden manipulation tactics in relationships\n"
                        "- Mind tricks your boss uses to control you at work\n"
                        "- Why your brain makes you spend money you dont have\n"
                        "- The dark reason you cant stop scrolling social media\n"
                        "- Why you freeze when someone disrespects you\n\n"
                        "VIRAL RULES:\n"
                        "- Hook = stops scrolling in under 2 seconds\n"
                        "- Fact = feels personal, about THEM specifically\n"
                        "- Must relate to dating, money, work or social media\n"
                        "- Language = 8th grade reading level max\n"
                        "- Title = power words: Secret, Dark, Never, Shocking, Hidden, Why\n\n"
                        "Return ONLY this JSON object:\n"
                        "{\n"
                        '  "topic": "specific relatable topic max 8 words",\n'
                        '  "niche": "one niche category",\n'
                        '  "hook": "shocking opener 6-8 words that stops scrolling",\n'
                        '  "fact": "2 short punchy sentences. no jargon. feels personal.",\n'
                        '  "why_it_matters": "2 sentences connecting to dating/money/work/social media",\n'
                        '  "real_example": "1 sentence specific American scenario eg at work on a date etc",\n'
                        '  "pexels_searches": ["term1", "term2", "term3", "term4", "term5"],\n'
                        '  "title": "YouTube title max 60 chars with power words",\n'
                        '  "description": "YouTube description max 200 chars with hashtags"\n'
                        "}\n\n"
                        "For pexels_searches: 5 different 2-3 word visual search terms "
                        "showing human emotions, brain, psychology, people reacting "
                        "eg: person thinking, brain neurons, stressed person, social media addiction, dark thoughts"
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
    print(f"✓ Niche: {topic['niche']}")
    print(f"✓ Hook: {topic['hook']}")
except Exception as e:
    print(f"❌ Step 1 failed: {e}")
    exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — Write Viral Script
# ══════════════════════════════════════════════════════════════════════════════
print("\n2️⃣  Writing viral script...")

try:
    script_res = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=groq_headers,
        json={
            "model": "llama-3.3-70b-versatile",
            "max_tokens": 700,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You write the most viral psychology YouTube Shorts in America. "
                        "Your scripts feel like a close friend revealing a dark secret. "
                        "BANNED WORDS: norepinephrine, cortisol, cognitive, consolidation, "
                        "phenomenon, neuroscience, psychological, dopamine, serotonin. "
                        "Write in plain American English. "
                        "Every single sentence makes the viewer desperate to hear the next. "
                        "Return ONLY the script. No labels. No titles. No formatting."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Write a VIRAL 45-50 second psychology script for US audience.\n\n"
                        f"Topic: {topic['topic']}\n"
                        f"Niche: {topic['niche']}\n"
                        f"Hook: {topic['hook']}\n"
                        f"Fact: {topic['fact']}\n"
                        f"Why it matters: {topic['why_it_matters']}\n"
                        f"Real example: {topic['real_example']}\n"
                        f"End with this EXACT CTA: {cta}\n\n"
                        "STRUCTURE:\n"
                        "1. Hook (2 sentences) — shock them in first 3 seconds\n"
                        "2. Dark reveal (3 sentences) — drop the fact like a secret\n"
                        "3. Real example (2 sentences) — scene they recognize from their own life\n"
                        "4. Personal impact (2 sentences) — why this affects THEM right now\n"
                        "5. Cliffhanger question (1 sentence) — makes them think\n"
                        "6. Exact CTA (1 sentence) — word for word as given\n\n"
                        "STRICT RULES:\n"
                        "- Every sentence MAX 8 words\n"
                        "- Use YOU and YOUR in every 2nd sentence\n"
                        "- Zero scientific terms\n"
                        "- Pause words allowed: dot dot dot (...) for dramatic effect\n"
                        "- 125-140 words total\n"
                        "- NO hey, welcome, today, hi guys\n"
                        "- Return ONLY the spoken script\n\n"
                        "PERFECT EXAMPLE OUTPUT:\n"
                        "Your brain is hiding something from you.\n"
                        "Right now. Every single day.\n"
                        "Here is the dark truth nobody tells you.\n"
                        "Your mind makes decisions 7 seconds before you do.\n"
                        "You think you chose that. You did not.\n"
                        "Think about the last argument you walked away from.\n"
                        "Your brain had already decided... before you opened your mouth.\n"
                        "This is why you keep repeating the same mistakes.\n"
                        "You are not broken. Your past is just running the show.\n"
                        "So who is actually in control of your life right now?\n"
                        f"{cta}"
                    )
                }
            ]
        },
        timeout=30
    )
    script_res.raise_for_status()
    script = script_res.json()["choices"][0]["message"]["content"].strip()
    # Remove any accidental quotes or labels
    script = script.strip('"').strip("'")
    print(f"✓ Script: {len(script.split())} words")
    print(f"✓ Preview: {' '.join(script.split()[:12])}...")
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
        f.write(f"NICHE: {topic['niche']}\n")
        f.write(f"HOOK: {topic['hook']}\n")
        f.write(f"CTA: {cta}\n\n")
        f.write("=" * 50 + "\n")
        f.write("VOICEOVER SCRIPT:\n")
        f.write("=" * 50 + "\n\n")
        f.write(script)

    with open("metadata.txt", "w", encoding="utf-8") as f:
        f.write(f"TITLE:\n{topic['title']}\n\n")
        f.write(f"DESCRIPTION:\n{topic['description']}\n\n")
        f.write(f"TOPIC:\n{topic['topic']}\n\n")
        f.write(f"NICHE:\n{topic['niche']}\n\n")
        f.write(f"HOOK:\n{topic['hook']}\n\n")
        f.write(f"CTA:\n{cta}\n\n")
        f.write(f"TAGS:\npsychology, dark psychology, mind tricks, brain facts, "
                f"human behavior, mental health, shorts, psychology facts, "
                f"mind blowing, self improvement\n\n")
        f.write(f"SCRIPT:\n{script}\n")
    print("✓ Files saved")
except Exception as e:
    print(f"❌ Step 3 failed: {e}")
    exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — Generate Voiceover (ElevenLabs - Josh voice)
# ══════════════════════════════════════════════════════════════════════════════
print("\n4️⃣  Generating voiceover (Josh - calm deep voice)...")

try:
    el_res = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
        headers={"xi-api-key": ELEVENLABS_API, "Content-Type": "application/json"},
        json={
            "text": script,
            "model_id": "eleven_flash_v2_5",
            "voice_settings": {
                "stability": 0.40,        # Natural variation, not monotone
                "similarity_boost": 0.78, # Clear & authentic
                "style": 0.25,            # Slight expressiveness
                "use_speaker_boost": True  # Cleaner audio
            }
        },
        timeout=60
    )
    if el_res.status_code != 200:
        print(f"❌ ElevenLabs error {el_res.status_code}: {el_res.text}")
        # Try with Adam voice as fallback
        print("   Trying Adam voice as fallback...")
        el_res = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgDQGcFmaJgB",
            headers={"xi-api-key": ELEVENLABS_API, "Content-Type": "application/json"},
            json={
                "text": script,
                "model_id": "eleven_flash_v2_5",
                "voice_settings": {
                    "stability": 0.40,
                    "similarity_boost": 0.78,
                    "style": 0.25,
                    "use_speaker_boost": True
                }
            },
            timeout=60
        )
        if el_res.status_code != 200:
            print(f"❌ Both voices failed: {el_res.text}")
            exit(1)

    with open("voiceover.mp3", "wb") as f:
        f.write(el_res.content)
    size = os.path.getsize("voiceover.mp3")
    if size < 1000:
        print("❌ Audio too small")
        exit(1)
    print(f"✓ Voiceover saved ({size:,} bytes)")
except Exception as e:
    print(f"❌ Step 4 failed: {e}")
    exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 5 — Get Audio Duration
# ══════════════════════════════════════════════════════════════════════════════
print("\n5️⃣  Getting audio duration...")

try:
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1', 'voiceover.mp3'],
        capture_output=True, text=True, timeout=10
    )
    audio_duration = float(result.stdout.strip())
    print(f"✓ Duration: {audio_duration:.1f}s")
except Exception:
    audio_duration = 50.0
    print(f"⚠️ Default: {audio_duration}s")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 6 — Download 5 Pexels Clips
# ══════════════════════════════════════════════════════════════════════════════
print("\n6️⃣  Downloading Pexels clips...")

def download_clip(query, filename):
    try:
        res = requests.get(
            f"https://api.pexels.com/videos/search"
            f"?query={urllib.parse.quote(query)}&per_page=15&orientation=portrait",
            headers={"Authorization": PEXELS_API},
            timeout=30
        )
        if res.status_code != 200:
            return False
        videos = res.json().get("videos", [])
        if not videos:
            return False
        random.shuffle(videos)
        for video in videos:
            if video.get("duration", 0) < 4:
                continue
            files = sorted(
                [f for f in video.get("video_files", []) if f.get("height", 0) >= 540],
                key=lambda x: x.get("height", 0), reverse=True
            )
            if not files:
                files = video.get("video_files", [])
            if not files:
                continue
            r = requests.get(files[0]["link"], timeout=60, stream=True)
            if r.status_code == 200:
                with open(filename, "wb") as f:
                    for chunk in r.iter_content(8192):
                        f.write(chunk)
                if os.path.getsize(filename) > 100000:
                    return True
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
    return False

searches = topic.get('pexels_searches', [
    'person thinking', 'brain neurons',
    'stressed person', 'social media',
    'dark psychology'
])

fallbacks = [
    'human thinking', 'mind psychology',
    'emotions person', 'brain science',
    'anxiety stress', 'social behavior',
    'person alone', 'decision making'
]

clips = []
clip_dur = audio_duration / 5

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
# STEP 7 — Process Clips (crop 9:16, resize 720x1280)
# ══════════════════════════════════════════════════════════════════════════════
print("\n7️⃣  Processing clips...")

processed = []
target_dur = audio_duration / max(len(clips), 1)

for i, clip in enumerate(clips):
    out = f"proc_{i}.mp4"
    cmd = (
        f'ffmpeg -i {clip} -t {target_dur + 0.5} '
        f'-vf "crop=ih*9/16:ih,scale=720:1280,setsar=1,fps=30" '
        f'-c:v libx264 -preset fast -crf 22 -an {out} -y 2>/dev/null'
    )
    if os.system(cmd) == 0 and os.path.exists(out) and os.path.getsize(out) > 10000:
        processed.append(out)
        print(f"   ✓ Clip {i+1} processed")
    else:
        print(f"   ⚠️ Clip {i+1} processing failed")

# Pad to at least 3 clips
while len(processed) < 3 and processed:
    processed.append(processed[0])

# ══════════════════════════════════════════════════════════════════════════════
# STEP 8 — Stitch Clips + Create Background
# ══════════════════════════════════════════════════════════════════════════════
print("\n8️⃣  Stitching clips...")

bg_video = "background.mp4"

if processed:
    with open("clips.txt", "w") as f:
        for p in processed:
            f.write(f"file '{p}'\n")

    result = os.system(
        f'ffmpeg -f concat -safe 0 -i clips.txt '
        f'-t {audio_duration + 1} '
        f'-c:v libx264 -preset fast -crf 22 '
        f'{bg_video} -y 2>/dev/null'
    )
    if result != 0 or not os.path.exists(bg_video) or os.path.getsize(bg_video) < 10000:
        print("   ⚠️ Stitch failed, using first clip")
        if processed:
            os.system(f'cp {processed[0]} {bg_video}')

if not os.path.exists(bg_video) or os.path.getsize(bg_video) < 10000:
    print("   Generating PIL fallback...")
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
        for _ in range(80):
            x,y = random.randint(0,720), random.randint(0,1280)
            r = random.randint(1,8)
            draw.ellipse([x-r,y-r,x+r,y+r],
                fill=(random.randint(60,150), random.randint(20,80), random.randint(180,255)))
        img.save("bg.jpg", quality=95)
        os.system(
            f'ffmpeg -loop 1 -i bg.jpg -t {audio_duration+1} '
            f'-c:v libx264 -tune stillimage -pix_fmt yuv420p {bg_video} -y 2>/dev/null'
        )
        print("   ✓ PIL fallback created")
    except Exception as e:
        print(f"❌ PIL failed: {e}")
        exit(1)

print(f"✓ Background ready ({os.path.getsize(bg_video):,} bytes)")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 9 — Generate Word-by-Word Subtitles
# ══════════════════════════════════════════════════════════════════════════════
print("\n9️⃣  Generating word-by-word subtitles...")

def srt_t(s):
    h,m = int(s//3600), int((s%3600)//60)
    sec, ms = int(s%60), int((s%1)*1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"

try:
    words = script.split()
    wps = len(words) / audio_duration
    # 3 words per subtitle for word-by-word effect
    chunk = 3
    groups = [words[i:i+chunk] for i in range(0, len(words), chunk)]
    srt = ""
    for i, g in enumerate(groups):
        s = (i * chunk) / wps
        e = min(((i+1) * chunk) / wps, audio_duration)
        srt += f"{i+1}\n{srt_t(s)} --> {srt_t(e)}\n{' '.join(g).upper()}\n\n"
    with open("subs.srt", "w", encoding="utf-8") as f:
        f.write(srt)
    print(f"✓ Subtitles ready ({len(groups)} lines)")
except Exception as e:
    print(f"⚠️ Subtitle error: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 10 — Final Video with Subtitles
# ══════════════════════════════════════════════════════════════════════════════
print("\n🔟  Rendering final video...")

# Subtitle style — bold yellow, TikTok style, word by word
sub_style = (
    "FontName=Arial Black,"
    "FontSize=20,"
    "PrimaryColour=&H00FFFF00,"
    "OutlineColour=&H00000000,"
    "BackColour=&H60000000,"
    "Bold=1,"
    "Outline=3,"
    "Shadow=1,"
    "Alignment=2,"
    "MarginV=100"
)

success = False

# Try with subtitles
if os.path.exists("subs.srt"):
    result = os.system(
        f'ffmpeg -i {bg_video} -i voiceover.mp3 '
        f'-c:v libx264 -c:a aac -b:a 192k '
        f"-vf \"scale=720:1280,subtitles=subs.srt:force_style='{sub_style}'\" "
        f'-pix_fmt yuv420p -shortest short.mp4 -y 2>/dev/null'
    )
    if result == 0 and os.path.exists("short.mp4") and os.path.getsize("short.mp4") > 10000:
        success = True
        print("✓ Video with subtitles created!")

# Fallback without subtitles
if not success:
    print("   Retrying without subtitles...")
    result = os.system(
        f'ffmpeg -i {bg_video} -i voiceover.mp3 '
        f'-c:v libx264 -c:a aac -b:a 192k '
        f'-vf "scale=720:1280" '
        f'-pix_fmt yuv420p -shortest short.mp4 -y 2>/dev/null'
    )
    if result == 0 and os.path.exists("short.mp4") and os.path.getsize("short.mp4") > 10000:
        success = True
        print("✓ Video created (no subtitles)")

if not success:
    print("❌ Video creation failed")
    exit(1)

size = os.path.getsize("short.mp4")
print(f"\n✅ ALL DONE! '{topic['title']}' 🎉")
print(f"📹 Video: {size:,} bytes ({size/1024/1024:.1f} MB)")
print(f"⏱️  Duration: ~{audio_duration:.0f} seconds")
print(f"\n📄 Output files:")
print(f"   - short.mp4     → upload to YouTube Shorts")
print(f"   - voiceover.mp3 → audio only")
print(f"   - script.txt    → voiceover + CTA")
print(f"   - metadata.txt  → title, description, tags")
