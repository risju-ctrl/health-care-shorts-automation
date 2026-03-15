#!/usr/bin/env python3
import os
import json
import requests
import time
import urllib.parse
from datetime import datetime

GROQ_API       = os.getenv("GROQ_API")
ELEVENLABS_API = os.getenv("ELEVENLABS_API")
ELEVENLABS_VOICE_ID = "pNInz6obpgDQGcFmaJgB"

print("🔑 Checking API keys...")
missing = []
if not GROQ_API:       missing.append("GROQ_API")
if not ELEVENLABS_API: missing.append("ELEVENLABS_API")
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
            "max_tokens": 600,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an expert viral YouTube Shorts content strategist "
                        "specializing in psychology content for US audiences aged 18-35. "
                        "You know exactly what makes people stop scrolling. "
                        "Return ONLY raw JSON, no markdown, no code fences."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        "Generate a unique viral psychology fact for a YouTube Shorts video targeting US audience.\n\n"
                        "NICHE FOCUS (pick one randomly):\n"
                        "- Dark psychology & manipulation tactics\n"
                        "- Mind control & persuasion\n"
                        "- Why people do weird things (behavioral psychology)\n"
                        "- Shocking brain science facts\n"
                        "- Social psychology & human behavior\n"
                        "- Cognitive biases that affect daily life\n"
                        "- Emotional intelligence & mental health\n"
                        "- Subconscious mind tricks\n\n"
                        "RULES FOR VIRAL US CONTENT:\n"
                        "- Hook must trigger curiosity or shock\n"
                        "- Fact must be counterintuitive or surprising\n"
                        "- Must relate to everyday American life\n"
                        "- Use simple language (8th grade reading level)\n"
                        "- Title must use power words (shocking, secret, never, always, why)\n\n"
                        "Return ONLY this JSON:\n"
                        "{\n"
                        '  "topic": "specific topic title",\n'
                        '  "niche": "which niche category this belongs to",\n'
                        '  "hook": "5-7 word shocking opener that stops scrolling",\n'
                        '  "fact": "the core psychology fact in 2 punchy sentences",\n'
                        '  "why_it_matters": "why this affects everyday American life in 2 sentences",\n'
                        '  "title": "viral YouTube title under 60 chars with power words",\n'
                        '  "description": "YouTube description under 200 chars with hashtags"\n'
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
except Exception as e:
    print(f"❌ Step 1 failed: {e}")
    exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — Write Voiceover Script (Groq)
# ══════════════════════════════════════════════════════════════════════════════
print("\n2️⃣  Writing voiceover script...")

try:
    script_res = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=groq_headers,
        json={
            "model": "llama-3.3-70b-versatile",
            "max_tokens": 600,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a top viral YouTube Shorts scriptwriter. "
                        "You write for US audiences aged 18-35. "
                        "Your scripts get millions of views. "
                        "Return ONLY the script text, nothing else."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Write a powerful 45-second psychology YouTube Shorts script for US audience.\n\n"
                        f"Topic: {topic['topic']}\n"
                        f"Niche: {topic['niche']}\n"
                        f"Hook: {topic['hook']}\n"
                        f"Fact: {topic['fact']}\n"
                        f"Why it matters: {topic['why_it_matters']}\n\n"
                        "SCRIPT RULES:\n"
                        "- Start with the hook — first 3 seconds must grab attention\n"
                        "- Use 'you' and 'your' to speak directly to viewer\n"
                        "- Short sentences. 5-8 words max per sentence.\n"
                        "- Build tension and curiosity in the middle\n"
                        "- Use simple everyday American language\n"
                        "- Add 1-2 real life examples Americans can relate to\n"
                        "- End with a question that makes them comment\n"
                        "- Exactly 120-140 words total\n"
                        "- NO intro like 'hey guys' or 'welcome back'\n"
                        "- Return ONLY the script text"
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
# STEP 3 — Save Script + Metadata as TXT files
# ══════════════════════════════════════════════════════════════════════════════
print("\n3️⃣  Saving script and metadata files...")

try:
    with open("script.txt", "w") as f:
        f.write(f"TOPIC: {topic['topic']}\n")
        f.write(f"NICHE: {topic['niche']}\n\n")
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
        f.write(f"TAGS:\npsychology, dark psychology, mind tricks, brain facts, "
                f"human behavior, cognitive bias, mental health, shorts\n\n")
        f.write(f"SCRIPT:\n{script}\n")
    print("✓ metadata.txt saved")

except Exception as e:
    print(f"❌ Step 3 failed: {e}")
    exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — Generate Voiceover Audio (ElevenLabs)
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
        print("❌ Audio file too small")
        exit(1)
    print(f"✓ Voiceover saved ({size} bytes)")
except Exception as e:
    print(f"❌ Step 4 failed: {e}")
    exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 5 — Generate Background Image (Pollinations with PIL fallback)
# ══════════════════════════════════════════════════════════════════════════════
print("\n5️⃣  Generating background image...")

image_path = "background.jpg"
image_success = False

models = ["turbo", "flux", "nanobanana"]
for model in models:
    for attempt in range(2):
        try:
            prompt_text = (
                f"cinematic vertical 9:16 psychology illustration about {topic['topic']}, "
                "dark moody aesthetic, neon blue and purple glowing tones, "
                "abstract brain silhouette, neural network patterns, "
                "dramatic cinematic lighting, ultra HD, no text, no faces, no people"
            )
            encoded = urllib.parse.quote(prompt_text)
            url = (f"https://image.pollinations.ai/prompt/{encoded}"
                   f"?width=720&height=1280&model={model}&nologo=true&seed={int(time.time())}")
            print(f"   Trying model={model} attempt {attempt+1}...")
            img_res = requests.get(url, timeout=90)
            if img_res.status_code == 200 and len(img_res.content) > 5000:
                with open(image_path, "wb") as f:
                    f.write(img_res.content)
                print(f"✓ Image saved ({os.path.getsize(image_path)} bytes)")
                image_success = True
                break
            else:
                print(f"   Failed ({img_res.status_code}), trying next...")
                time.sleep(5)
        except Exception as e:
            print(f"   Error: {e}")
            time.sleep(5)
    if image_success:
        break

if not image_success:
    print("   Generating with PIL fallback...")
    try:
        from PIL import Image, ImageDraw
        import random
        random.seed(int(time.time()))
        img = Image.new('RGB', (720, 1280), (8, 4, 25))
        draw = ImageDraw.Draw(img)
        for y in range(1280):
            r = int(8 + (y/1280)*15)
            g = int(4 + (y/1280)*8)
            b = int(25 + (y/1280)*55)
            draw.line([(0,y),(720,y)], fill=(r,g,b))
        for _ in range(60):
            x, y = random.randint(0,720), random.randint(0,1280)
            r2 = random.randint(1,8)
            draw.ellipse([x-r2,y-r2,x+r2,y+r2],
                fill=(random.randint(60,150), random.randint(20,80), random.randint(180,255)))
        img.save(image_path, quality=95)
        print(f"✓ Fallback image created ({os.path.getsize(image_path)} bytes)")
        image_success = True
    except Exception as e:
        print(f"❌ PIL fallback failed: {e}")
        exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 6 — Combine into Video (ffmpeg)
# ══════════════════════════════════════════════════════════════════════════════
print("\n6️⃣  Creating video...")

try:
    result = os.system(
        f'ffmpeg -loop 1 -i {image_path} -i voiceover.mp3 '
        f'-c:v libx264 -tune stillimage -c:a aac -b:a 192k '
        f'-pix_fmt yuv420p -shortest short.mp4 -y 2>/dev/null'
    )
    if result != 0 or not os.path.exists("short.mp4") or os.path.getsize("short.mp4") < 1000:
        print("❌ Video creation failed")
        exit(1)
    print(f"✓ Video created ({os.path.getsize('short.mp4')} bytes)")
except Exception as e:
    print(f"❌ Step 6 failed: {e}")
    exit(1)

print("\n⏭️  YouTube upload skipped for now.")
print(f"\n✅ ALL DONE! '{topic['title']}' created successfully! 🎉")
print(f"\n📄 Files created:")
print(f"   - short.mp4      (video)")
print(f"   - voiceover.mp3  (audio only)")
print(f"   - script.txt     (voiceover script)")
print(f"   - metadata.txt   (title, description, tags)")
