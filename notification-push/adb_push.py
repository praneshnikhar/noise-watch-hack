import subprocess
import sys


def push_notification(title, body):
    subprocess.run(
        [
            "adb", "shell", "cmd", "notification", "post",
            "-S", "noise_push",
            title, body,
        ],
        capture_output=True,
    )


def clear_notifications():
    subprocess.run(["adb", "shell", "cmd", "notification", "cancel-all"], capture_output=True)


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        push_notification(sys.argv[1], " ".join(sys.argv[2:]))
    else:
        push_notification("ADB Test", "This should show on your watch!")
        print("Sent test notification. Check your watch.")
