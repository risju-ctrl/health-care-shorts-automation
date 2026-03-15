import os
import requests
import json
import subprocess
import urllib.parse

GROQ_API = os.getenv("GROQ_API")
ELEVENLABS_API = os.getenv("ELEVENLABS_API")
WHISK_API = os.getenv("WHISK_API")
GROK_VIDEO_API = os.getenv("GROK_VIDEO_API")
PEXELS_API = os.getenv("PEXELS_API")

VOICE_ID = "TxGEqnHWrfWFTfGW9XjX"
TARGET_DURATION = 58

groq_headers = {
    "Authorization": f"Bearer {GROQ_API}",
    "Content-Type": "application/json"
}

print("Starting AI Psychology Shorts Pipeline")

# TITLE GENERATION

title_prompt = """
You are a YouTube Shorts strategist.

Audience:
United States viewers age 18–35.

Generate ONE viral psychology title.

Rules:
under 60 characters
curiosity driven
about human behavior
avoid scientific terms

Return only the title.
"""

res = requests.post(
    "https://api.groq.com/openai/v1/chat/completions",
    headers=groq_headers,
    json={
        "model": "llama-3.3-70b-versatile",
        "messages":[{"role":"user","content":title_prompt}]
    }
)

title = res.json()["choices"][0]["message"]["content"].strip()

print("Title:",title)

# SCRIPT GENERATION

script_prompt = f"""
Write a 58 second YouTube Shorts script.

Topic: {title}

Rules:
140-150 words
simple American English
second-person tone
emotional storytelling
no scientific terminology

Structure:
Hook
Insight
Example
Reflection ending

Return only the script text.
"""

res = requests.post(
    "https://api.groq.com/openai/v1/chat/completions",
    headers=groq_headers,
    json={
        "model":"llama-3.3-70b-versatile",
        "messages":[{"role":"user","content":script_prompt}]
    }
)

script = res.json()["choices"][0]["message"]["content"].strip()

with open("script.txt","w") as f:
    f.write(script)

print("Script created")

# SCENE GENERATION

scene_prompt = f"""
Convert this script into visual scenes.

Rules:
18-22 scenes
each scene equals 5-7 spoken words

Scene format:

Scene 1
Script Lines:
Scene Description:

Script:
{script}
"""

res = requests.post(
    "https://api.groq.com/openai/v1/chat/completions",
    headers=groq_headers,
    json={
        "model":"llama-3.3-70b-versatile",
        "messages":[{"role":"user","content":scene_prompt}]
    }
)

scene_text = res.json()["choices"][0]["message"]["content"]

descriptions = []

for line in scene_text.split("\n"):
    if "Scene Description:" in line:
        descriptions.append(line.replace("Scene Description:","").strip())

print("Scenes:",len(descriptions))

# IMAGE GENERATION

def generate_image(prompt,filename):

    payload = {
        "prompt":prompt,
        "size":"1024x1024"
    }

    r = requests.post(WHISK_API,json=payload)

    if r.status_code == 200:
        with open(filename,"wb") as f:
            f.write(r.content)
        return True

    return False

images=[]

for i,desc in enumerate(descriptions):

    prompt=f"""
{desc}

male character, short black hair, lean athletic build, dark casual clothing

cinematic anime film style
soft cel shading
dramatic lighting
psychological atmosphere
high detail
"""

    img=f"scene_{i}.png"

    if generate_image(prompt,img):
        images.append(img)

print("Images generated:",len(images))

# IMAGE TO VIDEO

def animate(image,output):

    files={"image":open(image,"rb")}

    data={
        "prompt":"subtle breathing motion cinematic scene"
    }

    r=requests.post(GROK_VIDEO_API,files=files,data=data)

    if r.status_code==200:
        with open(output,"wb") as f:
            f.write(r.content)
        return True

    return False

clips=[]

for i,img in enumerate(images):

    out=f"clip{i}.mp4"

    if animate(img,out):
        clips.append(out)

print("Animated clips:",len(clips))

# PEXELS FALLBACK

def download_pexels(query,filename):

    url=f"https://api.pexels.com/videos/search?query={urllib.parse.quote(query)}&per_page=10"

    res=requests.get(url,headers={"Authorization":PEXELS_API})

    data=res.json()

    for v in data["videos"]:

        files=v["video_files"]
        files.sort(key=lambda x:x["height"],reverse=True)

        link=files[0]["link"]

        r=requests.get(link)

        with open(filename,"wb") as f:
            f.write(r.content)

        if os.path.getsize(filename)>50000:
            return True

    return False

if len(clips) < 5:

    print("Using fallback clips")

    queries=["person thinking","emotional person","city night thinking"]

    for i,q in enumerate(queries):

        name=f"clip_fb{i}.mp4"

        if download_pexels(q,name):
            clips.append(name)

# VOICE GENERATION

voice_url=f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

res=requests.post(
    voice_url,
    headers={
        "xi-api-key":ELEVENLABS_API,
        "Content-Type":"application/json"
    },
    json={
        "text":script,
        "model_id":"eleven_flash_v2_5"
    }
)

with open("voice.mp3","wb") as f:
    f.write(res.content)

print("Voice generated")

# PROCESS CLIPS

processed=[]

for i,c in enumerate(clips):

    out=f"proc{i}.mp4"

    cmd=f'ffmpeg -y -i {c} -vf "crop=ih*9/16:ih,scale=720:1280" -t 4 -an {out}'

    os.system(cmd)

    processed.append(out)

# MERGE CLIPS

with open("list.txt","w") as f:

    for p in processed:
        f.write(f"file '{p}'\n")

subprocess.run("ffmpeg -y -f concat -safe 0 -i list.txt -c copy video.mp4",shell=True)

# FINAL VIDEO

subprocess.run(
    f'ffmpeg -y -i video.mp4 -i voice.mp3 -t {TARGET_DURATION} -vf scale=720:1280 short.mp4',
    shell=True
)

# METADATA

with open("metadata.txt","w") as f:

    f.write(f"Title:\n{title}\n\n")
    f.write("Tags:\npsychology, human behavior, dark psychology")

print("Video ready: short.mp4")
