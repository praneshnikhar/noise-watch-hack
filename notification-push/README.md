# Approach 2: Push Custom Notifications (No reverse-engineering needed)

## What we're doing
Instead of cracking the BLE protocol, we just push notifications through Android's
notification system. The Noise app already syncs phone notifications to the watch.

## Script: push_to_watch.py

Run this on your laptop — it sends notifications via `ntfy.sh` or a simple HTTP server
to your Android phone, which then shows them on the watch.

### Option A: Using ntfy.sh (simplest, no setup)

```python
# push_to_watch.py
import requests

def send_to_watch(title, message):
    """Send a notification that will appear on your Noise watch."""
    requests.post("https://ntfy.sh/YOUR_PRIVATE_TOPIC", 
        data=message.encode('utf-8'),
        headers={"Title": title, "Priority": "5"})

# Example usage
send_to_watch("Chatbot reply", "Sure! Here's the answer to your question...")
send_to_watch("Reminder", "Standing meeting in 5 minutes")
```

Steps:
1. Install [ntfy](https://ntfy.sh/) app on your Android phone from Play Store
2. Subscribe to a topic like `yourname_noisewatch` (pick something unique and long!)
3. Make sure ntfy notifications are enabled in Android settings
4. In NoiseFit app → enable notification sync for the ntfy app
5. Now any message pushed to that topic appears on your watch

### Option B: Direct ADB push (no internet needed)

```python
# adb_push.py
import subprocess

def push_notification(title, body):
    """Push notification via ADB — shows on phone + watch."""
    cmd = [
        "adb", "shell", "cmd", "notification", "post",
        "-S", "some_tag",
        title, body
    ]
    subprocess.run(cmd)

# Example
push_notification("Chatbot says:", "The weather today is 32°C, sunny.")
```

### Option C: Use Automate/Tasker on Android

Create a Tasker profile:
1. Trigger: HTTP Request received
2. Action: Create Notification → syncs to watch

Then POST to your phone's IP from your laptop:
```bash
curl http://192.168.1.100:8080/notify -d "title=Alert&body=Server is down"
```

## Wire this to your chatbot

```python
# chatbot_to_watch.py
import requests
from flask import Flask, request

app = Flask(__name__)
WATCH_TOPIC = "https://ntfy.sh/YOUR_PRIVATE_TOPIC"

def notify_watch(title, msg):
    requests.post(WATCH_TOPIC, data=msg.encode('utf-8'),
                  headers={"Title": title})

@app.route("/chatbot/reply", methods=["POST"])
def chatbot_reply():
    data = request.json
    response = your_chatbot_model.generate(data["message"])
    notify_watch("Bot reply:", response[:100])  # Truncate for watch screen
    return {"status": "sent"}

# Your chatbot responses now appear on your wrist
```

## Pros & Cons

| Approach | Effort | Reliability | Richness |
|----------|--------|-------------|----------|
| nRF + BLE reverse-engineering | High (hours-days) | Fragile | Full control — custom watch faces, animations |
| Notification push (ntfy/ADB) | Low (minutes) | Solid | Text only — title + body, ~30 chars visible |
