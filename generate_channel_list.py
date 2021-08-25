from telethon import TelegramClient
from telethon import types
import json


def get_config():
    with open("config.json") as f:
        config = json.load(f)
    return config


config = get_config()
SESSION_NAME = config["SESSION_NAME"]
API_ID = config["API_ID"]
API_HASH = config["API_HASH"]

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
with client:
    for dialog in client.iter_dialogs():
        if type(dialog.message.peer_id) == types.PeerChannel:
            print(f"Channel Name: {dialog.name} with ID: {dialog.message.peer_id.channel_id}")
