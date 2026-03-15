#!/usr/bin/env python3
import os
import json
import requests
import time
import urllib.parse
import random
from datetime import datetime

GROQ_API       = os.getenv("GROQ_API")
ELEVENLABS_API = os.getenv("ELEVENLABS_API")
ELEVENLABS_VOICE_ID = "pNInz6obpgDQGcFmaJgB"

# ── Rotating CTAs ─────────────────────────────────────────────────────────────
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
print(f"✓ CTA selected: {cta}")

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
                        "with 10 million subscribers. You specialize in psychology content "
                        "that goes viral with US audiences aged 18-35. "
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
                        "- Title needs power words: Secret, Dark, Never, Shocking, Why, Hidden\n"
                        "- Description must make people curious enough to watch\n\n"
                        "EXAMPLES OF GOOD HOOKS:\n"
                        "- 'Your brain is lying to you right now'\n"
                        "- 'Someone is using this on you today'\n"
                        "- 'You do this every day without knowing'\n"
                        "- 'This explains why you self-sabotage'\n\n"
                        "Return ONLY this JSON:\n"
                        "{\n"
                        '  "topic": "specific relatable topic title",\n'
                        '  "niche": "niche category",\n'
                        '  "hook": "shocking 6-8 word opener that stops scrolling",\n'
                        '  "fact": "the core psychology fact in 2 punchy personal sentences — no jargon",\n'
                        '  "why_it_matters": "how this affects dating/money/work/social life in 2 sentences",\n'
                        '  "real_example": "one specific American relatable scenario (e.g. at work, on a date, with friends)",\n'
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
except Exception as e:
    print(f"❌ Step 1 failed: {e}")
    exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — Write Viral Voiceover Script (Groq)
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
                        "Return ONLY the script text, nothing else, no labels, no titles."
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
                        f"Real example to include: {topic['real_example']}\n"
                        f"CTA to end with (use EXACTLY): {cta}\n\n"
                        "SCRIPT STRUCTURE:\n"
                        "1. Hook (1-2 sentences) — shock them immediately\n"
                        "2. The reveal (2-3 sentences) — drop the psychology fact simply\n"
                        "3. Real example (2-3 sentences) — relatable American scenario\n"
                        "4. Why it matters (2 sentences) — make it personal\n"
                        "5. CTA (1 sentence) — exact CTA provided above\n\n"
                        "STRICT RULES:\n"
                        "- Speak directly to viewer using YOU and YOUR constantly\n"
                        "- Maximum 8 words per sentence\n"
                        "- ZERO scientific jargon — talk like texting a friend\n"
                        "- Every sentence must make them want to hear the next\n"
                        "- Include the real example naturally in the script\n"
                        "- End with the EXACT CTA — do not change it\n"
                        "- Total: 120-140 words including CTA\n"
                        "- NO intro phrases like 'hey', 'welcome', 'today we'\n"
                        "- Return ONLY the script, nothing else\n\n"
                        "EXAMPLE OF GOOD STYLE:\n"
                        "Your brain is lying to you right now.\n"
                        "Every decision you make today is already decided.\n"
                        "You just think you chose it.\n"
                        "Here's the dark truth.\n"
                        "Your subconscious makes decisions 7 seconds before you do.\n"
                        "That text you sent at 2am? Already decided.\n"
                        "That job you almost took? Already rejected.\n"
                        "You are not in control. Your past experiences are.\n"
                        "This explains why you keep repeating the same mistakes.\n"
                        "So what decision is your brain making for you right now?\n"
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
# STEP 5 — Generate Background Image (Pollinations + PIL fallback)
# ══════════════════════════════════════════════════════════════════════════════
print("\n5️⃣  Generating background image...")

image_path = "background.jpg"
image_success = False

models = ["turbo", "flux", "nanobanana"]
for model in models:
    for attempt in range(2):
        try:
            prompt_text = (
                f"epic cinematic vertical 9:16 illustration about {topic['topic']}, "
                "3D rendered glowing brain deity character with expressive eyes, "
                "dark cosmic background with stars and galaxies, "
                "neon purple and gold energy swirling around brain, "
                "neural network patterns like constellations, "
                "dramatic god rays, electric sparks, ultra HD 8K, "
                "photorealistic, no text, no human faces, no people"
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
    print("   Generating PIL fallback...")
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
        img.save(image_path, quality=95)
        print(f"✓ Fallback image created ({os.path.getsize(image_path)} bytes)")
        image_success = True
    except Exception as e:
        print(f"❌ PIL fallback failed: {e}")
        exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 6 — Create Video (ffmpeg)
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
print(f"\n📄 Files:")
print(f"   - short.mp4      (video)")
print(f"   - voiceover.mp3  (audio)")
print(f"   - script.txt     (script + CTA)")
print(f"   - metadata.txt   (title, tags, description)")
