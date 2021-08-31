from datetime import datetime
from telegram_parser import get_message_entities
from telethon import TelegramClient, events
from telethon import types
from pprint import pprint
import asyncio
import json
import requests


def get_config():
    with open("config_test.json", encoding="utf-8") as f:
        config = json.load(f)
    return config


def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def generate_custom_message(original_message, entities):
    pair = "undetected"
    if entities["Pairs"]:
        pair = entities["Pairs"][0]
    else:
        if entities["Coins"]:
            pair = entities["Coins"][0]
    buy = entities["Buy"]
    tp = entities["TP"]
    sl = entities["SL"]

    raw_message = [
        f"Pair: {pair}",
        f"Buy: {buy}",
        f"TP: {tp}",
        f"SL: {sl}"
    ]
    entities_message = "\n".join(raw_message)

    original_message_text = original_message.message
    custom_message = "\n".join([original_message_text,
                                "-"*5,
                                "\n",
                                entities_message])
    original_message.message = custom_message
    return original_message


config = get_config()
SESSION_NAME = config["SESSION_NAME"]
API_ID = config["API_ID"]
API_HASH = config["API_HASH"]
SOURCE_CHANNEL_LIST = config["SOURCE_CHANNEL_LIST"]
DESTINATION_CHANNEL_ID = config["DESTINATION_CHANNEL_ID"]
HEALTH_CHECK_INTERVAL_SECOND = config["HEALTH_CHECK_INTERVAL_SECOND"]
IGNORE_LIST = config["IGNORE_LIST"]

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)


@client.on(events.NewMessage())
async def new_message_listener(event):
    def is_valid_message(message):
        for char in IGNORE_LIST:
            if char in message.lower():
                return False
        return True

    if type(event.message.peer_id) == types.PeerChannel:
        if is_valid_message(event.message.message):
            from_channel_id = event.message.peer_id.channel_id
            entities = get_message_entities(event.message.message)

            custom_message = generate_custom_message(event.message, entities)

            if from_channel_id in SOURCE_CHANNEL_LIST:
                time_utc = event.message.date.strftime("%Y-%m-%d %H:%M:%S")
                pprint({
                    "from_channel_id": from_channel_id,
                    "message": event.message.message,
                    "entities": entities,
                    "timestamp_utc": time_utc
                })
                await client.\
                    send_message(types.PeerChannel(DESTINATION_CHANNEL_ID),
                                 custom_message)


async def health_check(t):
    def get_status():
        try:
            r = requests.get("https://www.google.com/")
            if r.status_code == 200:
                return "available"
        except Exception:
            return "unavailable"

    while True:
        await asyncio.sleep(t)
        status = get_status()
        print(f"[{get_current_time()}] HEALTH CHECK STATUS: {status}")


async def main():
    async with client:
        print(f"[{get_current_time()}] START listening messages...")

        health_check_task = asyncio.create_task(
                                health_check(HEALTH_CHECK_INTERVAL_SECOND))
        await health_check_task

        await client.run_until_disconnected()


client.loop.run_until_complete(main())
