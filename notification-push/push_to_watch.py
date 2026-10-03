import requests
import sys

TOPIC = "CHANGE_ME_USE_SOMETHING_UNIQUE_AND_LONG"  # Pick a random string


def send_to_watch(title, message):
    resp = requests.post(
        f"https://ntfy.sh/{TOPIC}",
        data=message.encode("utf-8"),
        headers={"Title": title, "Priority": "5", "Tags": "robot"},
    )
    if resp.status_code == 200:
        print(f"✓ Sent: [{title}] {message}")
    else:
        print(f"✗ Failed: {resp.status_code}")


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        send_to_watch(sys.argv[1], " ".join(sys.argv[2:]))
    else:
        send_to_watch("Test", "Hello from Python! 👋")
