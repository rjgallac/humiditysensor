import time
import asyncio
import adafruit_dht
import board
import requests
from kasa import Discover
import os
import logging
from logging.handlers import RotatingFileHandler

# ----------------------------
# CONFIGURATION
# ----------------------------
DHT_PIN = board.D17

PLUG_IP = "192.168.1.58"
TAPO_USERNAME = os.environ.get("TAPO_USERNAME")
TAPO_PASSWORD = os.environ.get("TAPO_PASSWORD")

ON_THRESHOLD = 50
OFF_THRESHOLD = 40

POST_URL = "http://192.168.1.154:8000/reading"
READ_INTERVAL = 10

LOG_FILE = "/home/rjgallac/humiditysensor/humidity.log"
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 3                # keep last 3 logs

# ----------------------------
# LOGGING SETUP
# ----------------------------
logger = logging.getLogger("humidity_sensor")
logger.setLevel(logging.INFO)

# Rotating file handler
handler = RotatingFileHandler(LOG_FILE, maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Optional: also log to console (useful for manual runs)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

logger.info("=== Starting Humidity Sensor Script ===")

# ----------------------------
# SETUP
# ----------------------------
dht_device = adafruit_dht.DHT11(DHT_PIN)
device = None  # will be discovered lazily

async def get_device():
    global device
    if device is None:
        logger.info(f"Discovering Tapo device at {PLUG_IP}")
        device = await Discover.discover_single(
            PLUG_IP,
            username=TAPO_USERNAME,
            password=TAPO_PASSWORD
        )
    return device

async def update_plug(turn_on: bool):
    try:
        dev = await get_device()
        await dev.update()

        if turn_on and not dev.is_on:
            await dev.turn_on()
            logger.info(">>> Plug turned ON")

        elif not turn_on and dev.is_on:
            await dev.turn_off()
            logger.info(">>> Plug turned OFF")
    except Exception as e:
        logger.error(f"Error controlling plug: {e}")

# ----------------------------
# MAIN LOOP
# ----------------------------
async def main():
    while True:
        try:
            temperature_c = dht_device.temperature
            humidity = dht_device.humidity

            if humidity is None or temperature_c is None:
                raise RuntimeError("Sensor returned None")

            temperature_f = temperature_c * (9 / 5) + 32

            logger.info(f"Temp: {temperature_c:.1f} C / {temperature_f:.1f} F    Humidity: {humidity}%")

            # ---- Plug control
            if humidity >= ON_THRESHOLD:
                await update_plug(True)
            elif humidity <= OFF_THRESHOLD:
                await update_plug(False)

            # ---- Send reading
            # try:
            #     requests.post(
            #         POST_URL,
            #         data={"temp": temperature_c, "hum": humidity},
            #         timeout=3
            #     )
            # except requests.exceptions.RequestException as e:
            #     logger.warning(f"Error sending data: {e}")

        except RuntimeError as error:
            logger.warning(f"Sensor error: {error}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

        await asyncio.sleep(READ_INTERVAL)

asyncio.run(main())
