import asyncio
import struct
from bleak import BleakClient, BleakScanner


DEVICE_NAME = "Noise 6 Pro"  # Partial match
WATCH_ADDRESS = None  # Auto-discover
NOTIFICATION_CHAR_UUID = None  # Fill after sniffing — e.g. "0000fe02-..."
WATCHFACE_CHAR_UUID = None


async def discover_watch():
    print("Scanning for Noise watch...")
    devices = await BleakScanner.discover(timeout=10)
    for d in devices:
        if d.name and DEVICE_NAME.lower() in d.name.lower():
            print(f"Found: {d.name} [{d.address}]")
            return d.address
    print("Watch not found. Is it powered on and advertising?")
    return None


async def explore_services(address):
    """Print all GATT services and characteristics."""
    async with BleakClient(address) as client:
        print(f"\nConnected to {address}")
        for service in client.services:
            print(f"\nService: {service.uuid} ({service.description})")
            for char in service.characteristics:
                props = char.properties
                prop_str = []
                if "read" in props:
                    prop_str.append("READ")
                if "write" in props:
                    prop_str.append("WRITE")
                if "notify" in props:
                    prop_str.append("NOTIFY")
                if "write-without-response" in props:
                    prop_str.append("WRITE_NR")
                print(f"  └─ {char.uuid}: {' | '.join(prop_str)}")
                if "read" in props:
                    try:
                        val = await client.read_gatt_char(char.uuid)
                        print(f"      Value: {val.hex()}")
                    except Exception:
                        pass


async def send_raw_command(address, char_uuid, data: bytes):
    async with BleakClient(address) as client:
        await client.write_gatt_char(char_uuid, data, response=False)
        print(f"Sent {len(data)} bytes to {char_uuid}")


async def main():
    address = WATCH_ADDRESS or await discover_watch()
    if not address:
        return

    action = input("\n[a] Explore services  [s] Send test command  [q] Quit\n> ")

    if action == "a":
        await explore_services(address)
    elif action == "s":
        if NOTIFICATION_CHAR_UUID:
            await send_raw_command(address, NOTIFICATION_CHAR_UUID, b"\x01test")
        else:
            print("Set NOTIFICATION_CHAR_UUID first after exploring.")


if __name__ == "__main__":
    asyncio.run(main())
