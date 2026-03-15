#!/usr/bin/env python3
import os
import json
import requests
from datetime import datetime

# ── API Keys from GitHub Secrets ──────────────────────────────────────────────
CLAUDE_API     = os.getenv("CLAUDE_API")
ELEVENLABS_API = os.getenv("ELEVENLABS_API")
FREEPIK_API    = os.getenv("FREEPIK_API")

ELEVENLABS_VOICE_ID = "pNInz6obpgDQGcFmaJgB"

print("🚀 Starting Psychology Shorts automation pipeline...")
print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

claude_headers = {
    "x-api-key": CLAUDE_API,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json"
}

# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — Generate Psychology Topic (Claude)
# ══════════════════════════════════════════════════════════════════════════════
print("\n1️⃣  Generating psychology topic...")

topic_payload = {
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 500,
    "messages": [{
        "role": "user",
        "content": (
            "Generate a unique psychology fact for a YouTube Shorts video. "
            "Return ONLY a raw JSON object with these exact keys, no markdown, no code fences:\n"
            "{\n"
            '  "topic": "one-line topic title",\n'
            '  "hook": "5-word shocking opening line",\n'
            '  "fact": "the core psychology fact in 2 sentences",\n'
            '  "why_it_matters": "why this matters to everyday life in 2 sentences",\n'
            '  "title": "YouTube video title under 60 characters",\n'
            '  "description": "YouTube description under 200 characters"\n'
            "}"
        )
    }]
}

topic_res = requests.post(
    "https://api.anthropic.com/v1/messages",
    headers=claude_headers,
    json=topic_payload
)
topic_res.raise_for_status()
raw_topic = topic_res.json()["content"][0]["text"].strip()

if raw_topic.startswith("```"):
    raw_topic = raw_topic.split("```")[1]
    if raw_topic.startswith("json"):
        raw_topic = raw_topic[4:]

topic_data = json.loads(raw_topic.strip())
print(f"✓ Topic: {topic_data['topic']}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — Create Voiceover Script (Claude)
# ══════════════════════════════════════════════════════════════════════════════
print("\n2️⃣  Writing voiceover script with Claude...")

script_payload = {
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 500,
    "messages": [{
        "role": "user",
        "content": (
            f"Write a 45-second YouTube Shorts voiceover script about this psychology fact.\n\n"
            f"Topic: {topic_data['topic']}\n"
            f"Hook: {topic_data['hook']}\n"
            f"Fact: {topic_data['fact']}\n"
            f"Why it matters: {topic_data['why_it_matters']}\n\n"
            "Rules:\n"
            "- Start with the hook immediately — no intro\n"
            "- Conversational, calm tone\n"
            "- Short sentences. Easy to listen to.\n"
            "- End with a thought-provoking question for viewers\n"
            "- 120–140 words total\n"
            "- Return ONLY the script text, no labels or formatting"
        )
    }]
}

script_res = requests.post(
    "https://api.anthropic.com/v1/messages",
    headers=claude_headers,
    json=script_payload
)
script_res.raise_for_status()
script = script_res.json()["content"][0]["text"].strip()
print(f"✓ Script written ({len(script.split())} words)")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — Generate Voiceover Audio (ElevenLabs)
# ══════════════════════════════════════════════════════════════════════════════
print("\n3️⃣  Generating voiceover with ElevenLabs...")

el_url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
el_headers = {
    "xi-api-key": ELEVENLABS_API,
    "Content-Type": "application/json"
}
el_payload = {
    "text": script,
    "model_id": "eleven_monolingual_v1",
    "voice_settings": {
        "stability": 0.6,
        "similarity_boost": 0.85
    }
}

el_res = requests.post(el_url, headers=el_headers, json=el_payload)
el_res.raise_for_status()

audio_path = "voiceover.mp3"
with open(audio_path, "wb") as f:
    f.write(el_res.content)
print(f"✓ Voiceover saved: {audio_path}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — Generate Background Image (Freepik)
# ══════════════════════════════════════════════════════════════════════════════
print("\n4️⃣  Generating background image with Freepik...")

freepik_headers = {
    "x-freepik-api-key": FREEPIK_API,
    "Content-Type": "application/json"
}

image_prompt = (
    f"Cinematic vertical 9:16 illustration representing: {topic_data['topic']}. "
    "Dark moody psychology aesthetic, neon blue and purple tones, "
    "brain silhouette, thought bubbles, ultra HD, dramatic lighting, "
    "no text, no people's faces"
)

image_payload = {
    "prompt": image_prompt,
    "image": {
        "size": "portrait_9_16"
    },
    "styling": {
        "style": "photo",
        "color": "dark"
    }
}

img_res = requests.post(
    "https://api.freepik.com/v1/ai/text-to-image",
    headers=freepik_headers,
    json=image_payload
)
img_res.raise_for_status()
img_data = img_res.json()

image_url = img_data["data"][0]["url"]
img_file_res = requests.get(image_url)
image_path = "background.jpg"
with open(image_path, "wb") as f:
    f.write(img_file_res.content)
print(f"✓ Background image saved: {image_path}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 5 — Combine Image + Audio into Video (ffmpeg)
# ══════════════════════════════════════════════════════════════════════════════
print("\n5️⃣  Combining image + audio into video...")

video_path = "short.mp4"
os.system(
    f'ffmpeg -loop 1 -i {image_path} -i {audio_path} '
    f'-c:v libx264 -tune stillimage -c:a aac -b:a 192k '
    f'-pix_fmt yuv420p -shortest {video_path} -y'
)
print(f"✓ Video created: {video_path}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 6 — YouTube (Skipped for now)
# ══════════════════════════════════════════════════════════════════════════════
print("\n⏭️  YouTube upload skipped for now.")
print("\n✅ ALL DONE! Video created successfully! 🎉")
