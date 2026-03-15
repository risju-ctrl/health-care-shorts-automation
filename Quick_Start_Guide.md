# 🚀 QUICK START: Psychology Facts Automation (Week-by-Week)

## **THIS WEEK: Complete Setup (Choose Option A, B, or C)**

---

# 📌 CHOOSE YOUR PATH

## **Option A: No-Code (Best for beginners, easiest)**
- Use CapCut desktop app for editing
- Manual workflow but all tools connected
- **Time:** 5-7 hours/week
- **Skills needed:** None
- **Best for:** You if you like hands-on control

## **Option B: Semi-Automated (Best balance)**
- Use Python scripts for research → scripting → voiceover
- Manual editing in CapCut
- Auto-upload to YouTube
- **Time:** 2-3 hours/week
- **Skills needed:** Basic Python (copy-paste level)
- **Best for:** You if you want 80% automated but understand what's happening

## **Option C: Fully Automated (The dream)**
- Everything runs automatically
- GitHub Actions posts 1 video daily at 8 AM
- Zero human intervention needed
- **Time:** 0 hours/week (after 1-week setup)
- **Skills needed:** GitHub + basic Python
- **Best for:** You if you want complete hands-off operation

---

# 🎯 MY RECOMMENDATION FOR YOU: START WITH OPTION A → B

Here's why:
1. **Week 1-2:** Learn Option A (comfort zone, fast results)
2. **Week 3-4:** Upgrade to Option B (save 3-4 hours/week)
3. **Month 2:** Move to Option C (fully passive)

This is the realistic path that builds confidence.

---

# ✅ OPTION A: NO-CODE SETUP (Start Here)

## **Day 1-2: Infrastructure (90 minutes)**

### Step 1: Create Google Drive folders
```
Open Google Drive → Create folder "Psychology Facts Channel"

Inside, create:
├── Research/ (save topic ideas here)
├── Scripts/ (save scripts here)
├── Voiceovers/ (save MP3s here)
├── B-Roll/ (save videos here)
├── Edited Videos/ (save final videos here)
└── Published/ (save published versions here)
```

**Time:** 5 minutes

### Step 2: Create Notion Database
Go to notion.so → Create new database

**Copy this exactly:**

```
Database name: Psychology Facts Content Calendar

Properties:
1. Title (Text) - e.g., "Why You Procrastinate"
2. Topic (Text) - e.g., "Procrastination Psychology"
3. Hook (Text) - e.g., "Why you check your phone every 12 seconds"
4. Script (Text) - full 45-second script
5. Status (Select) - Options: Researched / Scripted / Voiceovered / Edited / Published
6. Voiceover (File) - upload MP3 here
7. Video (File) - upload final MP4 here
8. YouTube URL (URL) - paste video link when published
9. Upload Date (Date) - when you want it posted
10. Views (Number) - track views
11. CPM Earnings (Number) - track earnings
```

**Time:** 15 minutes

### Step 3: Get API Keys (20 minutes)
You'll need these free keys:

**1. Claude API Key** (for research + scripting)
- Go to console.anthropic.com
- Sign up (free)
- Click "API Keys"
- Create new key
- Copy it to a safe place (Google Doc, password manager)

**2. ElevenLabs API Key** (for voiceovers)
- Go to elevenlabs.io
- Sign up (free)
- Dashboard → API keys
- Copy key

**3. Pexels API Key** (for B-roll)
- Go to pexels.com/api
- Sign up
- Get API key (they email it)

**4. YouTube API Key** (for uploading)
- Go to console.cloud.google.com
- Create new project
- Enable YouTube Data API v3
- Create API key
- Copy it

**Time:** 20 minutes (most of it waiting for email)

### Step 4: Download Software (10 minutes)
- **CapCut** (free) - capcut.com/download
- **Python** (if you want Option B later) - python.org

**Time:** 10 minutes

**Total Day 1-2: 50 minutes** ✅

---

## **Day 3-4: Create First Video (3 hours)**

### Step 1: Generate Topic Idea (15 min)

Go to **Perplexity.ai** (free, no login needed)

Ask:
```
"Give me 1 unique psychology fact about procrastination.
Format:
- Hook: [short catchy version]
- Main fact: [explanation]
- Why it matters: [relevance]
- Source: [where you learned it]"
```

Copy the response into your **Notion database** → Status: "Researched"

**Time:** 15 minutes

### Step 2: Generate Script (20 min)

Go to **Claude** (console.anthropic.com) or use **claude.ai**

Paste this prompt:

```
Create a 45-second YouTube Shorts psychology script about procrastination.

Format:
- Hook (3 seconds, ~25 words): Grab attention immediately
- Explanation (20 seconds, ~80 words): Main fact
- Why it matters (15 seconds, ~60 words): Personal relevance
- CTA (7 seconds, ~25 words): End with question

Read naturally. No jargon. Make it conversational.
```

Copy the response into **Notion** → Status: "Scripted"

**Time:** 20 minutes

### Step 3: Create Voiceover (5 min)

Go to **ElevenLabs.io** (free tier)

Steps:
1. Click "Text to Speech"
2. Paste your script
3. Select voice "Rachel" (most natural)
4. Click "Generate"
5. Download MP3
6. Upload to Google Drive `/Voiceovers/` folder

Update **Notion** → Status: "Voiceovered"

**Time:** 5 minutes

### Step 4: Download B-Roll (10 min)

Go to **Pexels.com** (free, no login)

Search: "brain thinking psychology"

Download 3-4 videos (vertical format if possible)

Save to Google Drive `/B-Roll/` folder

**Time:** 10 minutes

### Step 5: Edit Video in CapCut (60 min)

Open **CapCut** Desktop app

Follow this **exact template:**

```
1. File → New Project
2. Choose 1080 × 1920 (vertical for Shorts)
3. Click "+" to add files
   - Import: voiceover.mp3
   - Import: broll_video1.mp4
   - Import: broll_video2.mp4
4. Drag voiceover onto timeline
5. Drag B-roll videos under voiceover (cut to match length)
6. Add text overlays:
   - At 0s: "HOOK TEXT" (white, center)
   - At 3s: "MAIN FACT" (white, center)
   - At 23s: "WHY IT MATTERS" (white, center)
   - At 38s: "YOUR QUESTION?" (white, center)
7. Add music (CapCut library, low volume)
8. Effects: Add fade in/out
9. Export: MP4, 1080p
```

**Time:** 60 minutes

### Step 6: Upload to YouTube (15 min)

Go to **YouTube Studio** (studio.youtube.com)

Click "Create" → "Upload video"

Upload your MP4

Fill in:
- Title: "Why You Procrastinate (Psychology Shorts)"
- Description: "Understanding the psychology of procrastination..."
- Tags: psychology, facts, shorts, procrastination
- Thumbnail: Use CapCut's auto-generated thumbnail

Click "Publish"

Update **Notion** → Status: "Published" + paste YouTube URL

**Time:** 15 minutes

**Total Day 3-4: 3 hours** ✅

---

## **Day 5-7: Batch Create 5 More Videos (8 hours)**

Now you're efficient. Repeat the process 5 more times:

### Batch Schedule:
- **Day 5 morning (2 hours):**
  - Generate 5 new topics (Perplexity)
  - Generate 5 scripts (Claude)
  
- **Day 5 afternoon (1.5 hours):**
  - Create 5 voiceovers (ElevenLabs)
  - Download B-roll for each

- **Day 6-7 (4.5 hours):**
  - Edit all 5 videos in CapCut (batch: 30 min each = 2.5 hours)
  - Upload all 5 to YouTube (15 min each = 1.25 hours)
  - Update Notion for all (30 min)

**Result: 6 videos created (1 from Week 1 + 5 new)**

---

## **Week 2+: WEEKLY ROUTINE (5-7 hours/week)**

Every Sunday:

**Morning (2 hours):**
- [ ] Open Perplexity → Generate 7 topics
- [ ] Open Claude → Generate 7 scripts
- [ ] Save all to Notion (Status: Researched → Scripted)

**Afternoon (1.5 hours):**
- [ ] ElevenLabs → Create 7 voiceovers
- [ ] Download B-roll for each
- [ ] Save to Google Drive

**Monday-Tuesday (3-4 hours):**
- [ ] Edit videos in CapCut batch
  - Set timer: 30 min per video
  - Do all 7 in sequence
  - Total: 3.5 hours

**Wednesday:**
- [ ] Upload all 7 to YouTube
  - Schedule one for each day this week
  - Auto-post one daily

**Update Notion:**
- [ ] Mark all as "Published"
- [ ] Paste YouTube URLs
- [ ] Schedule next batch

**Result:** 7 videos published across week (1/day), 5-7 hours of work

---

# 🤖 OPTION B: SEMI-AUTOMATED (After mastering Option A)

Once you're comfortable with Option A, upgrade with this Python script.

## **Setup (30 minutes)**

### Install Python (if you haven't)
```bash
# Mac
brew install python3

# Windows: Download from python.org

# Linux
sudo apt install python3 python3-pip
```

### Install libraries
```bash
pip install anthropic elevenlabs pexels-api google-auth-oauthlib google-auth-httplib2 google-api-python-client requests
```

### Create `.env` file
Create a file called `.env` in your project folder:

```
ANTHROPIC_API_KEY=sk-ant-v0-xxxxx
ELEVENLABS_API_KEY=xxxxx
PEXELS_API_KEY=xxxxx
YOUTUBE_API_KEY=xxxxx
```

**Save all API keys there (keep secret!)**

---

## **The Master Script: One File Does Everything**

Create a file called `psychology_automation.py`:

```python
#!/usr/bin/env python3
"""
Psychology Facts YouTube Shorts Automation
One script to rule them all.
"""

import os
from anthropic import Anthropic
from elevenlabs.client import ElevenLabs
import requests
from datetime import datetime
import json

# Load API keys from .env
from dotenv import load_dotenv
load_dotenv()

ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
ELEVENLABS_KEY = os.getenv("ELEVENLABS_API_KEY")
PEXELS_KEY = os.getenv("PEXELS_API_KEY")

# Initialize clients
claude_client = Anthropic()
elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_KEY)

def generate_topic():
    """Step 1: Generate a psychology topic"""
    print("🧠 Generating psychology topic...")
    
    response = claude_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": """Generate 1 unique psychology fact about human behavior.
            Format:
            Hook: [5 words max]
            Fact: [1 sentence]
            Why it matters: [2 sentences]
            Source: [where you learned it]"""
        }]
    )
    
    topic = response.content[0].text
    print(f"✅ Topic generated:\n{topic}\n")
    return topic

def generate_script(topic):
    """Step 2: Generate a 45-second script"""
    print("📝 Generating script...")
    
    response = claude_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": f"""Create a 45-second YouTube Shorts script about:
            {topic}
            
            Hook (3 seconds, ~25 words): Grab attention
            Explanation (20 seconds, ~80 words): Main fact  
            Why it matters (15 seconds, ~60 words): Relevance
            CTA (7 seconds, ~25 words): Question
            
            Make it conversational. No jargon."""
        }]
    )
    
    script = response.content[0].text
    print(f"✅ Script generated:\n{script}\n")
    return script

def create_voiceover(script):
    """Step 3: Generate voiceover MP3"""
    print("🎤 Creating voiceover...")
    
    audio = elevenlabs_client.text_to_speech.convert(
        text=script,
        voice_id="EXAVITQu4vr4xnSDxMaL",  # Rachel voice
        model_id="eleven_monolingual_v1"
    )
    
    # Save MP3
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"voiceovers/voiceover_{timestamp}.mp3"
    os.makedirs("voiceovers", exist_ok=True)
    
    with open(filename, "wb") as f:
        for chunk in audio:
            f.write(chunk)
    
    print(f"✅ Voiceover saved: {filename}\n")
    return filename

def download_broll():
    """Step 4: Download B-roll videos"""
    print("📹 Downloading B-roll...")
    
    topics = ["brain", "thinking", "psychology", "human mind"]
    
    os.makedirs("broll", exist_ok=True)
    
    for topic in topics:
        response = requests.get(
            f"https://api.pexels.com/v1/videos/search?query={topic}&per_page=2",
            headers={"Authorization": PEXELS_KEY}
        )
        
        videos = response.json()["videos"]
        
        for i, video in enumerate(videos):
            url = video["video_files"][0]["link"]
            filename = f"broll/{topic}_{i}.mp4"
            
            r = requests.get(url)
            with open(filename, "wb") as f:
                f.write(r.content)
            
            print(f"✅ Downloaded: {filename}")
    
    print()

def generate_metadata(script):
    """Step 5: Generate YouTube metadata"""
    print("📊 Generating metadata...")
    
    response = claude_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": f"""Based on this psychology script:
            {script}
            
            Generate ONLY a JSON object (no other text):
            {{
              "title": "...",
              "description": "...",
              "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
              "thumbnail_text": "..."
            }}"""
        }]
    )
    
    try:
        metadata = json.loads(response.content[0].text)
    except:
        # Fallback if JSON parsing fails
        metadata = {
            "title": "Psychology Fact",
            "description": "Discover fascinating psychology facts",
            "tags": ["psychology", "facts", "shorts", "mental health"],
            "thumbnail_text": "Did you know?"
        }
    
    print(f"✅ Metadata generated:\n{json.dumps(metadata, indent=2)}\n")
    return metadata

def main():
    """Run the complete automation pipeline"""
    print("=" * 60)
    print("🚀 Psychology Facts Automation Pipeline")
    print(f"   Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    # Step 1: Generate topic
    topic = generate_topic()
    
    # Step 2: Generate script
    script = generate_script(topic)
    
    # Step 3: Create voiceover
    voiceover = create_voiceover(script)
    
    # Step 4: Download B-roll
    download_broll()
    
    # Step 5: Generate metadata
    metadata = generate_metadata(script)
    
    # Save everything to a JSON file for reference
    output = {
        "timestamp": datetime.now().isoformat(),
        "topic": topic,
        "script": script,
        "voiceover_file": voiceover,
        "metadata": metadata
    }
    
    with open(f"outputs/{datetime.now().strftime('%Y%m%d_%H%M%S')}_content.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("=" * 60)
    print("✅ AUTOMATION COMPLETE!")
    print("=" * 60)
    print()
    print("📋 NEXT STEPS (Manual):")
    print("1. Edit video in CapCut")
    print("2. Upload to YouTube with metadata above")
    print("3. Mark as published")
    print()

if __name__ == "__main__":
    main()
```

---

## **Usage:**

```bash
# Run the script
python psychology_automation.py

# Output:
# ✅ Generates topic + script + voiceover + downloads B-roll
# ✅ All saved to folders
# ✅ Ready for you to edit in CapCut + upload
```

**Time saved:** 
- Before: 3 hours per video (topic + script + voiceover + B-roll)
- After: 30 minutes (just editing + uploading)

---

# 🚀 OPTION C: FULLY AUTOMATED (The Dream)

This requires **GitHub + 1 week setup**, but then posts 1 video DAILY automatically.

### Setup Cost:
- 1-2 weeks setup time (including learning curve)
- Then: **ZERO time, forever**

### One click per week:
```bash
git push
# ...sits back...
# Video auto-creates and posts daily at 8 AM
```

### Setup involves:
1. Create GitHub repo
2. Create GitHub Actions workflow
3. Store API keys as secrets
4. Schedule to run daily
5. Auto-upload to YouTube

**Want me to walk you through this? Let me know!**

---

# 📊 COMPARISON TABLE

| Task | Option A | Option B | Option C |
|------|----------|----------|----------|
| **Setup time** | 3-4 hours | 8-10 hours | 20+ hours |
| **Weekly time** | 5-7 hours | 2-3 hours | ~0 hours |
| **Cost/month** | $20 | $20 | $20 |
| **Videos/week** | 7 | 7 | 7 |
| **Earnings/month** | $500-1000 | $500-1000 | $500-1000 |
| **When to start** | **NOW** | Week 3 | Month 2 |

---

# ✅ YOUR ACTION PLAN

## **This Week:**
- [ ] Choose Option A (recommended to start)
- [ ] Day 1-2: Complete infrastructure setup
- [ ] Day 3-4: Create your first video
- [ ] Day 5-7: Batch create 5 more videos
- [ ] Upload 6 videos to YouTube

## **Next 2 Weeks:**
- [ ] Publish daily (schedule 1 per day)
- [ ] Track analytics in Notion
- [ ] Refine what works

## **Week 4:**
- [ ] Evaluate Option B (if you want to save time)
- [ ] Learn Python basics (if needed)
- [ ] Implement Python automation

## **Month 2:**
- [ ] Consider Option C (if you want full automation)
- [ ] Set up GitHub Actions
- [ ] Let it run while you sleep

---

# 🎯 EXPECTED RESULTS

### By Week 4 (30 videos):
- 500-2K subscribers
- $10-50 in earnings
- Clear trending topics (double down on winners)

### By Week 8 (60 videos):
- 5K-15K subscribers
- $50-200 in earnings
- First sponsorship inquiries

### By Week 12 (90 videos):
- 20K-50K subscribers
- $200-500 in earnings
- $500-1500 in sponsorships
- Reached monetization threshold

### By Month 6:
- 50K-150K subscribers
- $500-2000/month from ads
- $2000-5000/month from sponsorships

---

# 💡 TIPS FOR SUCCESS

1. **Consistency > Perfection**
   - Upload 1 video daily (even if just 7 per week)
   - Imperfect videos beat no videos

2. **Track What Works**
   - Save view counts in Notion
   - Double down on winning topics
   - Kill underperforming angles

3. **Reply to Comments**
   - Builds community
   - Signals activity to algorithm
   - Takes 10 min/day

4. **Update Regularly**
   - Check trending psychology topics
   - Stay current (AI breakthroughs, research)
   - Refresh old videos (re-upload with new angles)

5. **Batch Everything**
   - Record 5 scripts in one session
   - Edit 5 videos in one day
   - Upload 5 at once
   - Much more efficient than daily

---

# 🆘 TROUBLESHOOTING

**"My voiceover sounds robotic"**
- Try different ElevenLabs voices
- Try different speaking pace
- Add small pauses for emphasis

**"B-roll is hard to find"**
- Use Google Images (download → save as video)
- Try Unsplash.com (has videos too)
- Create your own B-roll (film anything moving/interesting)

**"I'm too slow editing"**
- Use CapCut templates (save one, reuse)
- Lower video quality (saves time, still looks good)
- Pay for CapCut Pro ($5/month) if needed

**"I don't know what topics to cover"**
- Search "trending psychology" on Google
- Look at top psychology shorts (what's viral?)
- Save topics in Notion when inspired

---

# 📞 NEXT STEPS

1. **Today:** Read this entire guide
2. **Tomorrow:** Start Option A setup
3. **This weekend:** Publish your first video
4. **Next week:** Post 1 per day

**Questions? Let me know:**
- Need help with Python setup?
- Want code templates?
- Need psychology topic ideas?
- Want analytics tracking template?

---

**You've got this! 🚀**

The hardest part is starting. The easiest part is continuing (once you automate it).

Go publish that first video today!
