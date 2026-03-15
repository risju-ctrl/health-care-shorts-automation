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

# ── Check all keys ─────────────────────────────────────────────────────────────
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
            "max_tokens": 500,
            "messages": [
                {"role": "system", "content": "You are a JSON generator. Return ONLY raw JSON, no markdown, no code fences."},
                {"role": "user", "content": (
                    "Generate a unique, mind-blowing psychology fact for YouTube Shorts.\n"
                    "Return ONLY this JSON:\n"
                    "{\n"
                    '  "topic": "short topic title",\n'
                    '  "hook": "shocking 5-word opener",\n'
                    '  "fact": "2 sentence psychology fact",\n'
                    '  "why_it_matters": "2 sentences why this matters",\n'
                    '  "title": "YouTube title under 60 chars",\n'
                    '  "description": "YouTube description under 200 chars",\n'
                    '  "image_prompt": "detailed cinematic image prompt for psychology visual, dark moody, neon purple blue, no text, no faces"\n'
                    "}"
                )}
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
                {"role": "system", "content": "You are a viral YouTube Shorts scriptwriter. Return ONLY the script, no labels."},
                {"role": "user", "content": (
                    f"Write a powerful 45-second psychology YouTube Shorts script.\n\n"
                    f"Topic: {topic['topic']}\n"
                    f"Hook: {topic['hook']}\n"
                    f"Fact: {topic['fact']}\n"
                    f"Why it matters: {topic['why_it_matters']}\n\n"
                    "Rules:\n"
                    "- Open with the hook immediately — no intro\n"
                    "- Calm, deep, authoritative tone\n"
                    "- Short punchy sentences\n"
                    "- Build curiosity throughout\n"
                    "- End with a powerful question that makes people think\n"
                    "- Exactly 120-140 words\n"
                    "- Return ONLY the script text"
                )}
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
# STEP 3 — Generate Voiceover (ElevenLabs)
# ══════════════════════════════════════════════════════════════════════════════
print("\n3️⃣  Generating voiceover...")

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
    print(f"❌ Step 3 failed: {e}")
    exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — Generate Background Image (Pollinations with fallback)
# ══════════════════════════════════════════════════════════════════════════════
print("\n4️⃣  Generating background image...")

image_path = "background.jpg"
image_success = False

# Try Pollinations with multiple models
models = ["turbo", "flux", "nanobanana"]
for model in models:
    for attempt in range(2):
        try:
            prompt_text = topic.get("image_prompt",
                f"cinematic psychology illustration {topic['topic']} dark moody neon purple blue brain"
            )
            encoded = urllib.parse.quote(prompt_text)
            url = f"https://image.pollinations.ai/prompt/{encoded}?width=720&height=1280&model={model}&nologo=true&seed={int(time.time())}"
            print(f"   Trying model={model} attempt {attempt+1}...")
            img_res = requests.get(url, timeout=90)
            if img_res.status_code == 200 and len(img_res.content) > 5000:
                with open(image_path, "wb") as f:
                    f.write(img_res.content)
                print(f"✓ Image saved with model={model} ({os.path.getsize(image_path)} bytes)")
                image_success = True
                break
            else:
                print(f"   Failed ({img_res.status_code}), trying next...")
                time.sleep(5)
        except Exception as e:
            print(f"   Error: {e}, trying next...")
            time.sleep(5)
    if image_success:
        break

# Fallback: Generate image with PIL if all APIs fail
if not image_success:
    print("   All image APIs failed — generating with PIL...")
    try:
        from PIL import Image, ImageDraw
        import random
        random.seed(42)
        img = Image.new('RGB', (720, 1280), (8, 4, 25))
        draw = ImageDraw.Draw(img)
        for y in range(1280):
            r = int(8 + (y/1280)*15)
            g = int(4 + (y/1280)*8)
            b = int(25 + (y/1280)*55)
            draw.line([(0,y),(720,y)], fill=(r,g,b))
        for _ in range(50):
            x,y = random.randint(0,720), random.randint(0,1280)
            r2 = random.randint(1,6)
            draw.ellipse([x-r2,y-r2,x+r2,y+r2], fill=(random.randint(60,150), random.randint(20,80), random.randint(180,255)))
        img.save(image_path, quality=95)
        print(f"✓ Fallback image created ({os.path.getsize(image_path)} bytes)")
        image_success = True
    except Exception as e:
        print(f"❌ PIL fallback failed: {e}")
        exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 5 — Combine into Video (ffmpeg)
# ══════════════════════════════════════════════════════════════════════════════
print("\n5️⃣  Creating video...")

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
    print(f"❌ Step 5 failed: {e}")
    exit(1)

print("\n⏭️  YouTube upload skipped for now.")
print(f"\n✅ ALL DONE! '{topic['title']}' created successfully! 🎉")
