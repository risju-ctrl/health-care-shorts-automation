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
ELEVENLABS_VOICE_ID = "pNInz6obpgDQGcFmaJgB"

# ── Rotating CTAs ──────────────────────────────────────────────────────────────
CTAS = [
    "Follow for more psychology facts that will blow your mind.",
    "Save this video. You'll want to watch it again.",
    "Comment below — did this change how you see yourself?",
    "Follow now. New psychology fact drops every day.",
    "Save this. Most people scroll past and never learn this.",
    "Comment 'mind blown' if this surprised you.",
    "Follow for daily psychology facts most people never learn.",
    "Save this video before you forget it.",
    "Comment below — have you ever experienced this yourself?",
    "Follow. Your mind will thank you later.",
]

# ── Check API Keys ─────────────────────────────────────────────────────────────
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
# STEP 1 — Generate Psychology Topic (Groq)
# ══════════════════════════════════════════════════════════════════════════════
print("\n1️⃣  Generating psychology topic...")

try:
    topic_res = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=groq_headers,
        json={
            "model": "llama-3.3-70b-versatile",
            "max_tokens": 700,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a viral YouTube Shorts psychologist content strategist "
                        "with 10 million subscribers targeting US audiences aged 18-35. "
                        "You NEVER use scientific jargon. You speak like a friend revealing "
                        "a shocking secret. Return ONLY raw JSON, no markdown, no code fences."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        "Generate a unique VIRAL psychology topic for YouTube Shorts targeting US audience aged 18-35.\n\n"
                        "PICK ONE NICHE RANDOMLY:\n"
                        "- Dark psychology & manipulation tactics people use on you daily\n"
                        "- Shocking things your brain does without you knowing\n"
                        "- Why you do embarrassing/weird things explained by science\n"
                        "- Mind tricks that work on everyone including you\n"
                        "- Social psychology secrets most people never discover\n"
                        "- Hidden biases controlling your decisions right now\n"
                        "- Emotional manipulation tactics used in relationships\n"
                        "- Subconscious patterns sabotaging your success\n\n"
                        "VIRAL CONTENT RULES:\n"
                        "- Hook must make someone STOP scrolling in 2 seconds\n"
                        "- Fact must feel PERSONAL — like it's about the viewer specifically\n"
                        "- Must connect to dating, money, work or social situations\n"
                        "- Use conversational language like texting a friend\n"
                        "- Title needs power words: Secret, Dark, Never, Shocking, Why, Hidden\n\n"
                        "Return ONLY this JSON:\n"
                        "{\n"
                        '  "topic": "specific relatable topic title",\n'
                        '  "niche": "niche category",\n'
                        '  "hook": "shocking 6-8 word opener that stops scrolling",\n'
                        '  "fact": "the core psychology fact in 2 punchy personal sentences, no jargon",\n'
                        '  "why_it_matters": "how this affects dating/money/work/social life in 2 sentences",\n'
                        '  "real_example": "one specific American relatable scenario",\n'
                        '  "pexels_search": "2-3 word Pexels video search query (e.g. human brain, dark thoughts, mind control)",\n'
                        '  "title": "viral YouTube title under 60 chars with power words",\n'
                        '  "description": "curiosity-driven YouTube description under 200 chars with hashtags"\n'
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
    print(f"✓ Niche: {topic['niche']}")
    print(f"✓ Pexels search: {topic['pexels_search']}")
except Exception as e:
    print(f"❌ Step 1 failed: {e}")
    exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — Write Viral Script (Groq)
# ══════════════════════════════════════════════════════════════════════════════
print("\n2️⃣  Writing voiceover script...")

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
                        "You are the writer behind the most viral psychology YouTube Shorts in the US. "
                        "Your scripts feel like a friend revealing a shocking secret. "
                        "You NEVER use scientific words like 'norepinephrine', 'cognitive', "
                        "'consolidation', or 'phenomenon'. "
                        "You speak in plain everyday American English. "
                        "Every sentence makes the viewer want to hear the next one. "
                        "Return ONLY the script text, nothing else."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Write a VIRAL 45-second psychology YouTube Shorts script for US audience.\n\n"
                        f"Topic: {topic['topic']}\n"
                        f"Niche: {topic['niche']}\n"
                        f"Hook: {topic['hook']}\n"
                        f"Fact: {topic['fact']}\n"
                        f"Why it matters: {topic['why_it_matters']}\n"
                        f"Real example: {topic['real_example']}\n"
                        f"CTA (EXACT): {cta}\n\n"
                        "SCRIPT STRUCTURE:\n"
                        "1. Hook (1-2 sentences) — shock them immediately\n"
                        "2. The reveal (2-3 sentences) — drop the psychology fact simply\n"
                        "3. Real example (2-3 sentences) — relatable American scenario\n"
                        "4. Why it matters (2 sentences) — make it personal\n"
                        "5. CTA (1 sentence) — exact CTA above\n\n"
                        "STRICT RULES:\n"
                        "- Speak directly using YOU and YOUR constantly\n"
                        "- Maximum 8 words per sentence\n"
                        "- ZERO scientific jargon\n"
                        "- Every sentence must create curiosity\n"
                        "- End with EXACT CTA — do not change it\n"
                        "- Total: 120-140 words\n"
                        "- NO 'hey', 'welcome', 'today we'\n"
                        "- Return ONLY the script\n\n"
                        "EXAMPLE STYLE:\n"
                        "Your brain is lying to you right now.\n"
                        "Every decision you make is already decided.\n"
                        "You just think you chose it.\n"
                        "Here is the dark truth.\n"
                        "Your subconscious decides 7 seconds before you do.\n"
                        "That text you sent at 2am? Already decided.\n"
                        "That job you almost took? Already rejected.\n"
                        "You are not in control. Your past is.\n"
                        "This is why you keep repeating the same mistakes.\n"
                        "So what is your brain deciding for you right now?\n"
                        "Follow for more psychology facts that will blow your mind."
                    )
                }
            ]
        },
        timeout=30
    )
    script_res.raise_for_status()
    script = script_res.json()["choices"][0]["message"]["content"].strip()
    print(f"✓ Script: {len(script.split())} words")
except Exception as e:
    print(f"❌ Step 2 failed: {e}")
    exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — Save Script + Metadata
# ══════════════════════════════════════════════════════════════════════════════
print("\n3️⃣  Saving script and metadata...")

try:
    with open("script.txt", "w") as f:
        f.write(f"TOPIC: {topic['topic']}\n")
        f.write(f"NICHE: {topic['niche']}\n")
        f.write(f"CTA: {cta}\n\n")
        f.write("=" * 50 + "\n")
        f.write("VOICEOVER SCRIPT:\n")
        f.write("=" * 50 + "\n\n")
        f.write(script)
    print("✓ script.txt saved")

    with open("metadata.txt", "w") as f:
        f.write(f"TITLE:\n{topic['title']}\n\n")
        f.write(f"DESCRIPTION:\n{topic['description']}\n\n")
        f.write(f"TOPIC:\n{topic['topic']}\n\n")
        f.write(f"NICHE:\n{topic['niche']}\n\n")
        f.write(f"HOOK:\n{topic['hook']}\n\n")
        f.write(f"REAL EXAMPLE:\n{topic['real_example']}\n\n")
        f.write(f"CTA:\n{cta}\n\n")
        f.write(f"TAGS:\npsychology, dark psychology, mind tricks, brain facts, "
                f"human behavior, cognitive bias, mental health, shorts, "
                f"psychology facts, mind blowing facts\n\n")
        f.write(f"SCRIPT:\n{script}\n")
    print("✓ metadata.txt saved")
except Exception as e:
    print(f"❌ Step 3 failed: {e}")
    exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — Generate Voiceover (ElevenLabs)
# ══════════════════════════════════════════════════════════════════════════════
print("\n4️⃣  Generating voiceover...")

try:
    el_res = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
        headers={"xi-api-key": ELEVENLABS_API, "Content-Type": "application/json"},
        json={
            "text": script,
            "model_id": "eleven_flash_v2_5",
            "voice_settings": {"stability": 0.6, "similarity_boost": 0.85}
        },
        timeout=60
    )
    if el_res.status_code != 200:
        print(f"❌ ElevenLabs error: {el_res.text}")
        exit(1)
    with open("voiceover.mp3", "wb") as f:
        f.write(el_res.content)
    size = os.path.getsize("voiceover.mp3")
    if size < 1000:
        print("❌ Audio too small")
        exit(1)
    print(f"✓ Voiceover saved ({size} bytes)")
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
        capture_output=True, text=True
    )
    audio_duration = float(result.stdout.strip())
    print(f"✓ Audio duration: {audio_duration:.1f} seconds")
except Exception as e:
    print(f"⚠️ Could not get duration, using 45s default: {e}")
    audio_duration = 45.0

# ══════════════════════════════════════════════════════════════════════════════
# STEP 6 — Download Pexels Background Video
# ══════════════════════════════════════════════════════════════════════════════
print("\n6️⃣  Downloading background video from Pexels...")

video_path = None
search_queries = [
    topic.get('pexels_search', 'human brain'),
    'psychology mind',
    'brain neurons',
    'dark thoughts',
    'human mind'
]

for query in search_queries:
    try:
        print(f"   Searching: '{query}'...")
        pexels_res = requests.get(
            f"https://api.pexels.com/videos/search?query={urllib.parse.quote(query)}&per_page=10&orientation=portrait",
            headers={"Authorization": PEXELS_API},
            timeout=30
        )
        if pexels_res.status_code != 200:
            print(f"   Pexels error: {pexels_res.status_code}")
            continue

        videos = pexels_res.json().get("videos", [])
        if not videos:
            print(f"   No results for '{query}'")
            continue

        random.shuffle(videos)
        for video in videos:
            video_files = video.get("video_files", [])
            hd_files = [f for f in video_files if f.get("quality") in ["hd", "sd"]]
            if not hd_files:
                hd_files = video_files
            if hd_files:
                hd_files.sort(key=lambda x: x.get("height", 0), reverse=True)
                video_url = hd_files[0]["link"]
                print(f"   Downloading video...")
                vid_res = requests.get(video_url, timeout=60, stream=True)
                if vid_res.status_code == 200:
                    raw_video = "raw_background.mp4"
                    with open(raw_video, "wb") as f:
                        for chunk in vid_res.iter_content(chunk_size=8192):
                            f.write(chunk)
                    if os.path.getsize(raw_video) > 100000:
                        video_path = raw_video
                        print(f"✓ Video downloaded ({os.path.getsize(raw_video)} bytes)")
                        break
        if video_path:
            break
    except Exception as e:
        print(f"   Error: {e}")
        continue

# ══════════════════════════════════════════════════════════════════════════════
# STEP 7 — Process Background Video
# ══════════════════════════════════════════════════════════════════════════════
processed_video = "processed_background.mp4"

if video_path:
    print("\n7️⃣  Processing background video...")
    try:
        result = os.system(
            f'ffmpeg -stream_loop -1 -i {video_path} '
            f'-t {audio_duration + 1} '
            f'-vf "crop=ih*9/16:ih,scale=720:1280,setsar=1" '
            f'-c:v libx264 -preset fast -crf 23 '
            f'-an {processed_video} -y 2>/dev/null'
        )
        if result == 0 and os.path.exists(processed_video):
            print(f"✓ Background video processed")
        else:
            video_path = None
    except Exception as e:
        print(f"⚠️ Error: {e}")
        video_path = None

if not video_path or not os.path.exists(processed_video):
    print("\n7️⃣  Generating PIL background...")
    try:
        from PIL import Image, ImageDraw
        random.seed(int(time.time()))
        img = Image.new('RGB', (720, 1280), (8, 4, 25))
        draw = ImageDraw.Draw(img)
        for y in range(1280):
            r = int(8 + (y/1280)*15)
            g = int(4 + (y/1280)*8)
            b = int(25 + (y/1280)*55)
            draw.line([(0,y),(720,y)], fill=(r,g,b))
        for _ in range(80):
            x, y = random.randint(0,720), random.randint(0,1280)
            r2 = random.randint(1,8)
            draw.ellipse([x-r2,y-r2,x+r2,y+r2],
                fill=(random.randint(60,150), random.randint(20,80), random.randint(180,255)))
        img.save("background.jpg", quality=95)
        os.system(
            f'ffmpeg -loop 1 -i background.jpg '
            f'-t {audio_duration + 1} '
            f'-c:v libx264 -tune stillimage -pix_fmt yuv420p '
            f'{processed_video} -y 2>/dev/null'
        )
        print(f"✓ PIL background created")
    except Exception as e:
        print(f"❌ PIL fallback failed: {e}")
        exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 8 — Generate Subtitle File (SRT)
# ══════════════════════════════════════════════════════════════════════════════
print("\n8️⃣  Generating subtitles...")

def seconds_to_srt_time(s):
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = int(s % 60)
    ms = int((s % 1) * 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"

try:
    words = script.split()
    words_per_second = len(words) / audio_duration
    chunk_size = 4
    chunks = [words[i:i+chunk_size] for i in range(0, len(words), chunk_size)]
    srt_content = ""
    for i, chunk in enumerate(chunks):
        start = (i * chunk_size) / words_per_second
        end = min(((i + 1) * chunk_size) / words_per_second, audio_duration)
        text = " ".join(chunk).upper()
        srt_content += f"{i+1}\n{seconds_to_srt_time(start)} --> {seconds_to_srt_time(end)}\n{text}\n\n"
    with open("subtitles.srt", "w") as f:
        f.write(srt_content)
    print(f"✓ Subtitles generated ({len(chunks)} lines)")
except Exception as e:
    print(f"⚠️ Subtitle generation failed: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 9 — Combine Video + Audio + Subtitles
# ══════════════════════════════════════════════════════════════════════════════
print("\n9️⃣  Creating final video...")

try:
    subtitle_filter = ""
    if os.path.exists("subtitles.srt"):
        subtitle_filter = (
            ",subtitles=subtitles.srt:force_style='"
            "FontName=Arial,"
            "FontSize=18,"
            "PrimaryColour=&H00FFFF00,"
            "OutlineColour=&H00000000,"
            "BackColour=&H80000000,"
            "Bold=1,"
            "Outline=2,"
            "Shadow=1,"
            "Alignment=2,"
            "MarginV=80"
            "'"
        )

    result = os.system(
        f'ffmpeg -i {processed_video} -i voiceover.mp3 '
        f'-c:v libx264 -c:a aac -b:a 192k '
        f'-vf "scale=720:1280{subtitle_filter}" '
        f'-pix_fmt yuv420p -shortest short.mp4 -y 2>/dev/null'
    )

    if result != 0 or not os.path.exists("short.mp4") or os.path.getsize("short.mp4") < 1000:
        print("   Retrying without subtitles...")
        result = os.system(
            f'ffmpeg -i {processed_video} -i voiceover.mp3 '
            f'-c:v libx264 -c:a aac -b:a 192k '
            f'-pix_fmt yuv420p -shortest short.mp4 -y 2>/dev/null'
        )

    if not os.path.exists("short.mp4") or os.path.getsize("short.mp4") < 1000:
        print("❌ Video creation failed")
        exit(1)

    print(f"✓ Final video created ({os.path.getsize('short.mp4')} bytes)")

except Exception as e:
    print(f"❌ Step 9 failed: {e}")
    exit(1)

print("\n⏭️  YouTube upload skipped for now.")
print(f"\n✅ ALL DONE! '{topic['title']}' created successfully! 🎉")
print(f"\n📄 Files:")
print(f"   - short.mp4      (final video with subtitles)")
print(f"   - voiceover.mp3  (audio only)")
print(f"   - script.txt     (script + CTA)")
print(f"   - metadata.txt   (title, tags, description)")
print(f"   - subtitles.srt  (subtitle file)")
