#!/usr/bin/env python3
import os
import json
import time
import requests
from datetime import datetime

# ── API Keys from GitHub Secrets ──────────────────────────────────────────────
GOOGLE_API    = os.getenv("GOOGLE_BARD_API")
CLAUDE_API    = os.getenv("CLAUDE_API")
ELEVENLABS_API = os.getenv("ELEVENLABS_API")
FREEPIK_API   = os.getenv("FREEPIK_API")

# ElevenLabs voice ID — "Adam" (male, calm & deep)
ELEVENLABS_VOICE_ID = "pNInz6obpgDQGcFmaJgB"

print("🚀 Starting Psychology Shorts automation pipeline...")
print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — Generate Psychology Topic (Google Gemini)
# ══════════════════════════════════════════════════════════════════════════════
print("\n1️⃣  Generating psychology topic...")

topic_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GOOGLE_API}"
topic_payload = {
    "contents": [{
        "parts": [{
            "text": (
                "Generate a unique psychology fact for a YouTube Shorts video. "
                "Return ONLY a JSON object with these keys:\n"
                "{\n"
                '  "topic": "one-line topic title",\n'
                '  "hook": "5-word shocking opening line",\n'
                '  "fact": "the core psychology fact in 2 sentences",\n'
                '  "why_it_matters": "why this matters to everyday life in 2 sentences",\n'
                '  "title": "YouTube video title under 60 characters",\n'
                '  "description": "YouTube description under 200 characters"\n'
                "}\n"
                "Do not include markdown or code fences. Return raw JSON only."
            )
        }]
    }]
}

topic_res = requests.post(topic_url, json=topic_payload)
topic_res.raise_for_status()
raw_topic = topic_res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

# Strip accidental markdown fences
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

claude_headers = {
    "x-api-key": CLAUDE_API,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json"
}
claude_payload = {
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

claude_res = requests.post(
    "https://api.anthropic.com/v1/messages",
    headers=claude_headers,
    json=claude_payload
)
claude_res.raise_for_status()
script = claude_res.json()["content"][0]["text"].strip()
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
# STEP 4 — Generate Video with Freepik AI
# ══════════════════════════════════════════════════════════════════════════════
print("\n4️⃣  Generating video with Freepik...")

freepik_headers = {
    "x-freepik-api-key": FREEPIK_API,
    "Content-Type": "application/json"
}

# Generate a vertical AI image for the Short
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

# Download the generated image
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
# STEP 6 — Upload to YouTube
# ══════════════════════════════════════════════════════════════════════════════
print("\n6️⃣  Uploading to YouTube...")

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

youtube_creds_json = os.getenv("YOUTUBE_CREDENTIALS")
creds_data = json.loads(youtube_creds_json)
creds = Credentials(
    token=creds_data["token"],
    refresh_token=creds_data["refresh_token"],
    token_uri="https://oauth2.googleapis.com/token",
    client_id=creds_data["client_id"],
    client_secret=creds_data["client_secret"]
)

youtube = build("youtube", "v3", credentials=creds)

request_body = {
    "snippet": {
        "title": topic_data["title"],
        "description": topic_data["description"] + "\n\n#psychology #shorts #facts #mindset",
        "tags": ["psychology", "shorts", "facts", "mind", "brain", "science"],
        "categoryId": "27"  # Education
    },
    "status": {
        "privacyStatus": "public",
        "selfDeclaredMadeForKids": False
    }
}

media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True)
upload = youtube.videos().insert(
    part="snippet,status",
    body=request_body,
    media_body=media
)

response = None
while response is None:
    status, response = upload.next_chunk()
    if status:
        print(f"   Uploading... {int(status.progress() * 100)}%")

print(f"✓ Video uploaded! ID: {response['id']}")
print(f"✓ URL: https://youtube.com/shorts/{response['id']}")

print("\n✅ ALL DONE! Psychology Short published successfully! 🎉")
