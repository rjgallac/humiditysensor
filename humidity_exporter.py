import time
import asyncio
import adafruit_dht
import board
import logging
from logging.handlers import RotatingFileHandler
from prometheus_client import start_http_server, Gauge

# ----------------------------
# CONFIG
# ----------------------------
DHT_PIN = board.D17
READ_INTERVAL = 10
METRICS_PORT = 9105

LOG_FILE = "/home/rjgallac/humiditysensor/humidity.log"

# ----------------------------
# LOGGING
# ----------------------------
logger = logging.getLogger("humidity_exporter")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# ----------------------------
# PROMETHEUS METRICS
# ----------------------------
temperature_c = Gauge("room_temperature_celsius", "Room temperature in Celsius")
humidity_pct = Gauge("room_humidity_percent", "Room humidity percentage")

# ----------------------------
# SENSOR
# ----------------------------
dht_device = adafruit_dht.DHT11(DHT_PIN)

async def main():
    logger.info("Starting Prometheus exporter")
    start_http_server(METRICS_PORT)

    while True:
        try:
            temp = dht_device.temperature
            hum = dht_device.humidity

            if temp is None or hum is None:
                raise RuntimeError("Sensor returned None")

            temperature_c.set(temp)
            humidity_pct.set(hum)

            logger.info(f"Temp={temp:.1f}C  Humidity={hum}%")

        except Exception as e:
            logger.warning(f"Sensor error: {e}")

        await asyncio.sleep(READ_INTERVAL)

asyncio.run(main())
