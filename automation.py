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
                        "You are a viral YouTube Shorts psychology content strategist "
                        "targeting US audiences aged 18-35. "
                        "You NEVER use scientific jargon. "
                        "Return ONLY raw JSON, no markdown, no code fences."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        "Generate a unique VIRAL psychology topic for YouTube Shorts.\n\n"
                        "PICK ONE NICHE RANDOMLY:\n"
                        "- Dark psychology & manipulation tactics\n"
                        "- Shocking things your brain does without you knowing\n"
                        "- Why you do embarrassing/weird things\n"
                        "- Mind tricks that work on everyone\n"
                        "- Social psychology secrets\n"
                        "- Hidden biases controlling your decisions\n"
                        "- Emotional manipulation in relationships\n"
                        "- Subconscious patterns sabotaging success\n\n"
                        "Return ONLY this JSON:\n"
                        "{\n"
                        '  "topic": "specific relatable topic",\n'
                        '  "niche": "niche category",\n'
                        '  "hook": "shocking 6-8 word opener",\n'
                        '  "fact": "2 punchy personal sentences, no jargon",\n'
                        '  "why_it_matters": "2 sentences about dating/money/work",\n'
                        '  "real_example": "one specific American relatable scenario",\n'
                        '  "pexels_searches": ["search term 1", "search term 2", "search term 3", "search term 4", "search term 5"],\n'
                        '  "title": "viral YouTube title under 60 chars",\n'
                        '  "description": "YouTube description under 200 chars with hashtags"\n'
                        "}\n\n"
                        "For pexels_searches: provide 5 DIFFERENT 2-3 word search terms "
                        "related to the topic (e.g. 'human brain', 'dark thoughts', "
                        "'mind control', 'people thinking', 'stress anxiety')"
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
    print(f"✓ Pexels searches: {topic['pexels_searches']}")
except Exception as e:
    print(f"❌ Step 1 failed: {e}")
    exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — Write Viral Script
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
                        "NEVER use: norepinephrine, cognitive, consolidation, phenomenon, cortisol. "
                        "Speak plain everyday American English. "
                        "Every sentence makes the viewer want to hear the next. "
                        "Return ONLY the script text, nothing else."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Write a VIRAL 45-50 second psychology YouTube Shorts script.\n\n"
                        f"Topic: {topic['topic']}\n"
                        f"Niche: {topic['niche']}\n"
                        f"Hook: {topic['hook']}\n"
                        f"Fact: {topic['fact']}\n"
                        f"Why it matters: {topic['why_it_matters']}\n"
                        f"Real example: {topic['real_example']}\n"
                        f"CTA (EXACT): {cta}\n\n"
                        "SCRIPT STRUCTURE:\n"
                        "1. Hook (1-2 sentences) — shock immediately\n"
                        "2. Reveal (2-3 sentences) — drop the fact simply\n"
                        "3. Real example (2-3 sentences) — relatable scenario\n"
                        "4. Why it matters (2 sentences) — make it personal\n"
                        "5. CTA — use EXACT CTA above\n\n"
                        "RULES:\n"
                        "- Use YOU and YOUR constantly\n"
                        "- Max 8 words per sentence\n"
                        "- ZERO jargon\n"
                        "- Build curiosity every sentence\n"
                        "- 120-140 words total\n"
                        "- NO 'hey', 'welcome', 'today we'\n"
                        "- Return ONLY script text\n\n"
                        "EXAMPLE:\n"
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
print("\n3️⃣  Saving files...")

try:
    with open("script.txt", "w") as f:
        f.write(f"TOPIC: {topic['topic']}\n")
        f.write(f"NICHE: {topic['niche']}\n")
        f.write(f"CTA: {cta}\n\n")
        f.write("=" * 50 + "\n")
        f.write("VOICEOVER SCRIPT:\n")
        f.write("=" * 50 + "\n\n")
        f.write(script)

    with open("metadata.txt", "w") as f:
        f.write(f"TITLE:\n{topic['title']}\n\n")
        f.write(f"DESCRIPTION:\n{topic['description']}\n\n")
        f.write(f"TOPIC:\n{topic['topic']}\n\n")
        f.write(f"NICHE:\n{topic['niche']}\n\n")
        f.write(f"HOOK:\n{topic['hook']}\n\n")
        f.write(f"CTA:\n{cta}\n\n")
        f.write(f"TAGS:\npsychology, dark psychology, mind tricks, brain facts, "
                f"human behavior, mental health, shorts, psychology facts\n\n")
        f.write(f"SCRIPT:\n{script}\n")
    print("✓ Files saved")
except Exception as e:
    print(f"❌ Step 3 failed: {e}")
    exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — Generate Voiceover
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
    print(f"✓ Duration: {audio_duration:.1f}s")
except Exception:
    audio_duration = 50.0
    print(f"⚠️ Using default: {audio_duration}s")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 6 — Download Multiple Pexels Clips
# ══════════════════════════════════════════════════════════════════════════════
print("\n6️⃣  Downloading Pexels video clips...")

def download_pexels_clip(query, filename, duration_needed):
    """Download a single Pexels video clip"""
    try:
        res = requests.get(
            f"https://api.pexels.com/videos/search?query={urllib.parse.quote(query)}&per_page=15&orientation=portrait",
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
            # Filter videos that are long enough
            if video.get("duration", 0) < 3:
                continue
            files = video.get("video_files", [])
            # Prefer HD portrait files
            good_files = [f for f in files if f.get("height", 0) >= 720]
            if not good_files:
                good_files = files
            if not good_files:
                continue

            good_files.sort(key=lambda x: x.get("height", 0), reverse=True)
            url = good_files[0]["link"]

            vid_res = requests.get(url, timeout=60, stream=True)
            if vid_res.status_code == 200:
                with open(filename, "wb") as f:
                    for chunk in vid_res.iter_content(chunk_size=8192):
                        f.write(chunk)
                if os.path.getsize(filename) > 50000:
                    return True
    except Exception as e:
        print(f"   Error downloading '{query}': {e}")
    return False

# Download 5 different clips
searches = topic.get('pexels_searches', [
    'human brain', 'dark thoughts', 'mind control',
    'people thinking', 'stress anxiety'
])

# Fallback searches if topic ones fail
fallback_searches = [
    'psychology', 'human mind', 'thinking person',
    'brain neurons', 'mental health', 'emotions',
    'social interaction', 'person alone thinking'
]

downloaded_clips = []
clip_duration = audio_duration / 5  # Each clip ~1/5 of total duration

for i, query in enumerate(searches[:5]):
    filename = f"clip_{i}.mp4"
    print(f"   Downloading clip {i+1}/5: '{query}'...")
    success = download_pexels_clip(query, filename, clip_duration)
    if success:
        downloaded_clips.append(filename)
        print(f"   ✓ Clip {i+1} downloaded")
    else:
        # Try fallback
        fallback = fallback_searches[i % len(fallback_searches)]
        print(f"   Trying fallback: '{fallback}'...")
        success = download_pexels_clip(fallback, filename, clip_duration)
        if success:
            downloaded_clips.append(filename)
            print(f"   ✓ Clip {i+1} downloaded (fallback)")

print(f"✓ Downloaded {len(downloaded_clips)}/5 clips")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 7 — Process & Stitch Clips Together
# ══════════════════════════════════════════════════════════════════════════════
print("\n7️⃣  Processing and stitching clips...")

processed_clips = []
clip_target_duration = audio_duration / max(len(downloaded_clips), 1)

for i, clip in enumerate(downloaded_clips):
    output = f"processed_clip_{i}.mp4"
    try:
        # Crop to 9:16, resize to 720x1280, trim to needed duration
        cmd = (
            f'ffmpeg -i {clip} '
            f'-t {clip_target_duration + 0.5} '
            f'-vf "crop=ih*9/16:ih,scale=720:1280,setsar=1,fps=30" '
            f'-c:v libx264 -preset fast -crf 23 '
            f'-an {output} -y 2>/dev/null'
        )
        if os.system(cmd) == 0 and os.path.exists(output):
            processed_clips.append(output)
            print(f"   ✓ Clip {i+1} processed")
    except Exception as e:
        print(f"   ⚠️ Clip {i+1} failed: {e}")

# If not enough clips, duplicate what we have
while len(processed_clips) < 3 and processed_clips:
    processed_clips.append(processed_clips[0])

# ══════════════════════════════════════════════════════════════════════════════
# STEP 8 — Create Background Video
# ══════════════════════════════════════════════════════════════════════════════
print("\n8️⃣  Creating background video...")

background_video = "background_combined.mp4"

if processed_clips:
    # Write concat file
    with open("concat_list.txt", "w") as f:
        for clip in processed_clips:
            f.write(f"file '{clip}'\n")

    # Concatenate all clips
    result = os.system(
        f'ffmpeg -f concat -safe 0 -i concat_list.txt '
        f'-c:v libx264 -preset fast -crf 23 '
        f'-t {audio_duration + 1} '
        f'{background_video} -y 2>/dev/null'
    )

    if result != 0 or not os.path.exists(background_video):
        print("   ⚠️ Concat failed, using first clip only")
        if processed_clips:
            os.system(f'cp {processed_clips[0]} {background_video}')

if not os.path.exists(background_video) or os.path.getsize(background_video) < 1000:
    print("   Generating PIL fallback background...")
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
            f'{background_video} -y 2>/dev/null'
        )
        print("✓ PIL fallback background created")
    except Exception as e:
        print(f"❌ PIL fallback failed: {e}")
        exit(1)

print(f"✓ Background video ready ({os.path.getsize(background_video)} bytes)")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 9 — Generate Word-by-Word Subtitles (ASS format for styling)
# ══════════════════════════════════════════════════════════════════════════════
print("\n9️⃣  Generating word-by-word subtitles...")

def seconds_to_ass_time(s):
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = s % 60
    return f"{h}:{m:02d}:{sec:05.2f}"

try:
    words = script.split()
    total_words = len(words)
    words_per_second = total_words / audio_duration

    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,52,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,3,2,2,20,20,120,1
Style: Highlight,Arial,52,&H0000FFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,3,2,2,20,20,120,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    ass_events = ""
    # Group words into chunks of 2-3 for word-by-word effect
    chunk_size = 2
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = words[i:i+chunk_size]
        chunks.append(chunk)

    for i, chunk in enumerate(chunks):
        start_time = (i * chunk_size) / words_per_second
        end_time = min(((i + 1) * chunk_size) / words_per_second, audio_duration)
        text = " ".join(chunk).upper()

        # Highlight current words in yellow, rest in white
        ass_events += (
            f"Dialogue: 0,{seconds_to_ass_time(start_time)},"
            f"{seconds_to_ass_time(end_time)},Highlight,,0,0,0,,"
            f"{{{\\\\c&H00FFFF&}}}{text}\n"
        )

    with open("subtitles.ass", "w") as f:
        f.write(ass_header + ass_events)

    print(f"✓ Word-by-word subtitles generated ({len(chunks)} chunks)")

except Exception as e:
    print(f"⚠️ ASS subtitle failed, trying SRT: {e}")
    # Fallback to SRT
    try:
        def srt_time(s):
            h,m = int(s//3600), int((s%3600)//60)
            sec, ms = int(s%60), int((s%1)*1000)
            return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"

        words = script.split()
        wps = len(words) / audio_duration
        chunks = [words[i:i+3] for i in range(0, len(words), 3)]
        srt = ""
        for i, chunk in enumerate(chunks):
            s = (i*3)/wps
            e = min(((i+1)*3)/wps, audio_duration)
            srt += f"{i+1}\n{srt_time(s)} --> {srt_time(e)}\n{' '.join(chunk).upper()}\n\n"
        with open("subtitles.srt", "w") as f:
            f.write(srt)
        print(f"✓ SRT subtitles generated")
    except Exception as e2:
        print(f"⚠️ Subtitle generation failed: {e2}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 10 — Combine Everything into Final Video
# ══════════════════════════════════════════════════════════════════════════════
print("\n🔟  Creating final video...")

try:
    # Try with ASS subtitles first (best quality word-by-word)
    if os.path.exists("subtitles.ass"):
        result = os.system(
            f'ffmpeg -i {background_video} -i voiceover.mp3 '
            f'-c:v libx264 -c:a aac -b:a 192k '
            f'-vf "scale=720:1280,ass=subtitles.ass" '
            f'-pix_fmt yuv420p -shortest short.mp4 -y 2>/dev/null'
        )
    else:
        result = 1

    # Try SRT subtitles
    if result != 0 and os.path.exists("subtitles.srt"):
        print("   Trying SRT subtitles...")
        result = os.system(
            f'ffmpeg -i {background_video} -i voiceover.mp3 '
            f'-c:v libx264 -c:a aac -b:a 192k '
            f'-vf "scale=720:1280,subtitles=subtitles.srt:force_style=\'FontSize=18,PrimaryColour=&H00FFFF00,Bold=1,Outline=2,Alignment=2,MarginV=80\'" '
            f'-pix_fmt yuv420p -shortest short.mp4 -y 2>/dev/null'
        )

    # Final fallback — no subtitles
    if result != 0 or not os.path.exists("short.mp4") or os.path.getsize("short.mp4") < 1000:
        print("   Creating video without subtitles...")
        result = os.system(
            f'ffmpeg -i {background_video} -i voiceover.mp3 '
            f'-c:v libx264 -c:a aac -b:a 192k '
            f'-pix_fmt yuv420p -shortest short.mp4 -y 2>/dev/null'
        )

    if not os.path.exists("short.mp4") or os.path.getsize("short.mp4") < 1000:
        print("❌ Video creation failed")
        exit(1)

    final_size = os.path.getsize("short.mp4")
    print(f"✓ Final video created ({final_size} bytes / {final_size/1024/1024:.1f} MB)")

except Exception as e:
    print(f"❌ Step 10 failed: {e}")
    exit(1)

print("\n⏭️  YouTube upload skipped for now.")
print(f"\n✅ ALL DONE! '{topic['title']}' created! 🎉")
print(f"\n📄 Files:")
print(f"   - short.mp4      (final video ~45-55s)")
print(f"   - voiceover.mp3  (audio)")
print(f"   - script.txt     (script + CTA)")
print(f"   - metadata.txt   (title, tags, description)")
