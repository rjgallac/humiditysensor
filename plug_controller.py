import asyncio
import os
from kasa import Discover
import logging

PLUG_IP = "192.168.1.58"
TAPO_USERNAME = os.environ["TAPO_USERNAME"]
TAPO_PASSWORD = os.environ["TAPO_PASSWORD"]

logging.basicConfig(level=logging.INFO)
device = None

async def get_device():
    global device
    if device is None:
        device = await Discover.discover_single(
            PLUG_IP,
            username=TAPO_USERNAME,
            password=TAPO_PASSWORD
        )
    return device

async def turn_on():
    dev = await get_device()
    await dev.update()
    if not dev.is_on:
        await dev.turn_on()
        logging.info("Plug ON")

async def turn_off():
    dev = await get_device()
    await dev.update()
    if dev.is_on:
        await dev.turn_off()
        logging.info("Plug OFF")
