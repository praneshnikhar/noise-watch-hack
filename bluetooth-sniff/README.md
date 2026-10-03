# Approach 1: Reverse-Engineer NoiseFit BLE Protocol

## What we're doing
The NoiseFit app talks to your watch over Bluetooth Low Energy (BLE) using GATT services.
We'll sniff that communication, find which characteristics control the display, and learn
how to send our own data directly — bypassing the official app.

## Tools needed
- [nRF Connect for Mobile](https://play.google.com/store/apps/details?id=no.nordicsemi.android.mcp) (Android)
- Your Noise 6 Pro Max paired to your phone
- (Optional) ESP32 or nRF52840 dongle for deeper sniffing

## Step 1: Explore GATT services

1. Install nRF Connect on your Android phone
2. Open NoiseFit app, pair your watch normally
3. Close NoiseFit app (kill it from recents)
4. Open nRF Connect, scan for devices
5. Find your watch (usually named "Noise 6 Pro..." or similar)
6. Connect to it
7. The "Unknown Service" tab shows all discovered GATT services and characteristics

Look for:
- **Device Information** (0x180A) — f/w version, model, serial
- **Unknown services** — these are the custom/proprietary ones Noise uses
- Characteristics with **WRITE** or **NOTIFY** properties — these are commands

## Step 2: Log the traffic

1. In nRF Connect, open your watch's device page
2. Scroll to the bottom, find "Bonded" settings
3. Tap the three dots → "Show log"
4. Re-open NoiseFit app and let it sync with the watch
5. Watch the log — you'll see Write and Notify commands flowing

What to capture:
- **Watch face change**: Switch watch faces in the app and note which characteristic gets written to
- **Notification**: Send yourself a test notification and see what gets written
- **Find my phone**: Tap this and see what the watch sends back

## Step 3: Identify the protocol

Typical Noise watch protocol patterns I've seen:
- Watch face data: long byte array written to a custom characteristic (UUID often in range `0000FExx-...`)
- Notifications: JSON or binary struct with title/body
- Commands: single-byte writes (0x01 = vibration, 0x02 = camera capture, etc.)

## Step 4: Write your own data

With the characteristics identified, you can:
1. Use nRF Connect's "Write" button directly to test sending bytes
2. Build a Python script using `bleak` or `pybluez2` to automate it

```python
# Example: ble_control.py — will need actual UUIDs from sniffing
import asyncio
from bleak import BleakClient

DEVICE_ADDRESS = "XX:XX:XX:XX:XX:XX"  # Your watch's MAC
WATCHFACE_CHAR = "0000fe01-0000-1000-8000-00805f9b34fb"  # Example, find yours
NOTIFICATION_CHAR = "0000fe02-0000-1000-8000-00805f9b34fb"

async def send_custom_watchface(client, image_bytes):
    await client.write_gatt_char(WATCHFACE_CHAR, image_bytes, response=True)

async def send_notification(client, title, body):
    # Construct the notification packet (format varies — sniff first!)
    data = f"{title}|{body}".encode('utf-8')
    await client.write_gatt_char(NOTIFICATION_CHAR, data, response=True)

async def main():
    async with BleakClient(DEVICE_ADDRESS) as client:
        await send_notification(client, "Hello", "From Python!")

asyncio.run(main())
```

## Step 5: ESP32 as a permanent controller

Once you crack the protocol, flash an ESP32 that acts as your permanent watch controller:

```
ESP32 → BLE commands → Noise Watch
   ↑
  WiFi
   ↑
Your laptop / home server / chatbot
```

The ESP32 pairs with the watch once and exposes an HTTP endpoint that your
chatbot/laptop can POST to.
