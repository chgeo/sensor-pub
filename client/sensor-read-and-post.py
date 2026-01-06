import asyncio
from bleak import BleakClient
from datetime import datetime
import requests
import os
import time
from dotenv import load_dotenv

# -------------------------------
# Load .env from one directory up
# -------------------------------
dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path)

# -------------------------------
# Environment variables
# -------------------------------
USERNAME = os.getenv("updater-user")
PASSWORD = os.getenv("updater-password")
ENDPOINT = os.getenv("server-url")+"/sensors/update/data"
ADDRESS = os.getenv("device-address")  # BLE device address from .env

CHAR_UUID = "0000fff2-0000-1000-8000-00805f9b34fb"

# -------------------------------
# Retry configuration
# -------------------------------
BLE_RETRIES = 3
HTTP_RETRIES = 3
BASE_DELAY = 2  # seconds, base for exponential backoff

# -------------------------------
# Read sensor data with exponential backoff
# -------------------------------
async def read_sensor():
    for attempt in range(1, BLE_RETRIES + 1):
        try:
            async with BleakClient(ADDRESS) as client:
                data = await client.read_gatt_char(CHAR_UUID)

                temp_raw = int.from_bytes(data[0:2], "little", signed=True)
                hum_raw  = int.from_bytes(data[2:4], "little")

                return {
                    "temperature": round(temp_raw / 100, 1),
                    "humidity": round(hum_raw / 100, 1),
                    "time": datetime.utcnow().isoformat()
                }
        except Exception as e:
            delay = BASE_DELAY * (2 ** (attempt - 1))
            print(f"❌ BLE read attempt {attempt} failed: {e}. Retrying in {delay}s...")
            if attempt < BLE_RETRIES:
                time.sleep(delay)
            else:
                raise

# -------------------------------
# Send data via HTTP POST with exponential backoff
# -------------------------------
def send_data(payload):
    for attempt in range(1, HTTP_RETRIES + 1):
        try:
            response = requests.post(
                ENDPOINT,
                json=payload,
                auth=(USERNAME, PASSWORD),
                verify=False  # temporary: ignore SSL cert issues
            )
            response.raise_for_status()
            print("✅ Data sent successfully")
            return
        except requests.RequestException as e:
            delay = BASE_DELAY * (2 ** (attempt - 1))
            print(f"❌ HTTP POST attempt {attempt} failed: {e}. Retrying in {delay}s...")
            if attempt < HTTP_RETRIES:
                time.sleep(delay)
            else:
                raise

# -------------------------------
# Main async loop
# -------------------------------
async def main():
    try:
        value = await read_sensor()
        print("🌡️ Measurement:", value)
        send_data(value)
    except Exception as e:
        print("❌ Error during measurement or sending:", e)

# -------------------------------
# Entry point
# -------------------------------
if __name__ == "__main__":
    asyncio.run(main())

