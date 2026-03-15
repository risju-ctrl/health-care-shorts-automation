#!/usr/bin/env python3
import os
import json
import requests
from datetime import datetime
import urllib.parse

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

print("\n🚀 Starting Psychology Shorts automation pipeline...")
print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

groq_headers = {
    "Authorization": f"Bearer {GROQ_API}",
    "Content-Type": "application/json"
}

# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — Generate Psychology Topic (Groq)
# ══════════════════════════════════════════════════════════════════════════════
print("\n1️⃣  Generating psychology topic...")

try:
    topic_payload = {
        "model": "llama-3.3-70b-versatile",
        "max_tokens": 500,
        "messages": [
            {
                "role": "system",
                "content": "You are a JSON generator. Return ONLY raw JSON, no markdown, no code fences, no explanation."
            },
            {
                "role": "user",
                "content": (
                    "Generate a unique psychology fact for a YouTube Shorts video. "
                    "Return ONLY a raw JSON object with these exact keys:\n"
                    "{\n"
                    '  "topic": "one-line topic title",\n'
                    '  "hook": "5-word shocking opening line",\n'
                    '  "fact": "the core psychology fact in 2 sentences",\n'
                    '  "why_it_matters": "why this matters to everyday life in 2 sentences",\n'
                    '  "title": "YouTube video title under 60 characters",\n'
                    '  "description": "YouTube description under 200 characters"\n'
                    "}"
                )
            }
        ]
    }

    topic_res = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=groq_headers,
        json=topic_payload,
        timeout=30
    )
    print(f"   Groq status: {topic_res.status_code}")
    topic_res.raise_for_status()

    raw_topic = topic_res.json()["choices"][0]["message"]["content"].strip()

    if raw_topic.startswith("```"):
        raw_topic = raw_topic.split("```")[1]
        if raw_topic.startswith("json"):
            raw_topic = raw_topic[4:]

    topic_data = json.loads(raw_topic.strip())
    print(f"✓ Topic: {topic_data['topic']}")

except requests.exceptions.HTTPError as e:
    print(f"❌ Groq API error: {e}")
    print(f"   Response: {topic_res.text}")
    exit(1)
except json.JSONDecodeError as e:
    print(f"❌ Failed to parse JSON: {e}")
    print(f"   Raw response: {raw_topic}")
    exit(1)
except Exception as e:
    print(f"❌ Unexpected error in Step 1: {e}")
    exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — Create Voiceover Script (Groq)
# ══════════════════════════════════════════════════════════════════════════════
print("\n2️⃣  Writing voiceover script...")

try:
    script_payload = {
        "model": "llama-3.3-70b-versatile",
        "max_tokens": 500,
        "messages": [
            {
                "role": "system",
                "content": "You are a YouTube Shorts scriptwriter. Return ONLY the script text, nothing else."
            },
            {
                "role": "user",
                "content": (
                    f"Write a 45-second YouTube Shorts voiceover script about this psychology fact.\n\n"
                    f"Topic: {topic_data['topic']}\n"
                    f"Hook: {topic_data['hook']}\n"
                    f"Fact: {topic_data['fact']}\n"
                    f"Why it matters: {topic_data['why_it_matters']}\n\n"
                    "Rules:\n"
                    "- Start with the hook immediately\n"
                    "- Conversational, calm tone\n"
                    "- Short sentences\n"
                    "- End with a thought-provoking question\n"
                    "- 120-140 words total\n"
                    "- Return ONLY the script, no labels"
                )
            }
        ]
    }

    script_res = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=groq_headers,
        json=script_payload,
        timeout=30
    )
    print(f"   Groq status: {script_res.status_code}")
    script_res.raise_for_status()

    script = script_res.json()["choices"][0]["message"]["content"].strip()
    print(f"✓ Script written ({len(script.split())} words)")

except requests.exceptions.HTTPError as e:
    print(f"❌ Groq API error: {e}")
    print(f"   Response: {script_res.text}")
    exit(1)
except Exception as e:
    print(f"❌ Unexpected error in Step 2: {e}")
    exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — Generate Voiceover Audio (ElevenLabs)
# ══════════════════════════════════════════════════════════════════════════════
print("\n3️⃣  Generating voiceover with ElevenLabs...")

try:
    el_url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    el_headers = {
        "xi-api-key": ELEVENLABS_API,
        "Content-Type": "application/json"
    }
    el_payload = {
        "text": script,
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {
            "stability": 0.6,
            "similarity_boost": 0.85
        }
    }

    el_res = requests.post(el_url, headers=el_headers, json=el_payload, timeout=60)
    print(f"   ElevenLabs status: {el_res.status_code}")

    if el_res.status_code != 200:
        print(f"❌ ElevenLabs error: {el_res.text}")
        exit(1)

    audio_path = "voiceover.mp3"
    with open(audio_path, "wb") as f:
        f.write(el_res.content)

    if os.path.getsize(audio_path) < 1000:
        print("❌ Voiceover file too small — something went wrong")
        exit(1)

    print(f"✓ Voiceover saved ({os.path.getsize(audio_path)} bytes)")

except requests.exceptions.Timeout:
    print("❌ ElevenLabs timed out")
    exit(1)
except Exception as e:
    print(f"❌ Unexpected error in Step 3: {e}")
    exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — Generate Background Image (Pollinations - FREE)
# ══════════════════════════════════════════════════════════════════════════════
print("\n4️⃣  Generating background image with Pollinations...")

try:
    image_prompt = (
        f"Cinematic vertical psychology illustration representing: {topic_data['topic']}. "
        "Dark moody aesthetic, neon blue and purple tones, "
        "brain silhouette, thought bubbles, ultra HD, dramatic lighting, "
        "no text, no faces"
    )

    encoded_prompt = urllib.parse.quote(image_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=720&height=1280&nologo=true"

    print(f"   Fetching image from Pollinations...")
    img_res = requests.get(image_url, timeout=60)

    if img_res.status_code != 200:
        print(f"❌ Pollinations error: {img_res.status_code}")
        exit(1)

    image_path = "background.jpg"
    with open(image_path, "wb") as f:
        f.write(img_res.content)

    if os.path.getsize(image_path) < 1000:
        print("❌ Image file too small — something went wrong")
        exit(1)

    print(f"✓ Background image saved ({os.path.getsize(image_path)} bytes)")

except requests.exceptions.Timeout:
    print("❌ Pollinations timed out")
    exit(1)
except Exception as e:
    print(f"❌ Unexpected error in Step 4: {e}")
    exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 5 — Combine Image + Audio into Video (ffmpeg)
# ══════════════════════════════════════════════════════════════════════════════
print("\n5️⃣  Combining image + audio into video...")

try:
    video_path = "short.mp4"
    result = os.system(
        f'ffmpeg -loop 1 -i {image_path} -i {audio_path} '
        f'-c:v libx264 -tune stillimage -c:a aac -b:a 192k '
        f'-pix_fmt yuv420p -shortest {video_path} -y'
    )

    if result != 0:
        print("❌ ffmpeg failed to create video")
        exit(1)

    if not os.path.exists(video_path) or os.path.getsize(video_path) < 1000:
        print("❌ Video file missing or too small")
        exit(1)

    print(f"✓ Video created ({os.path.getsize(video_path)} bytes)")

except Exception as e:
    print(f"❌ Unexpected error in Step 5: {e}")
    exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 6 — YouTube (Skipped for now)
# ══════════════════════════════════════════════════════════════════════════════
print("\n⏭️  YouTube upload skipped for now.")
print("\n✅ ALL DONE! Video created successfully! 🎉")
