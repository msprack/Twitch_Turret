#!/usr/bin/env python3
from dotenv import load_dotenv
import os
import requests
import json
BASE_API = "https://api.twitch.tv/helix/"

DISCORD_HOOK = os.getenv("DISCORD_HOOK")
AUTH_TOKEN=os.getenv("AUTH_TOKEN")
CLIENT_ID = os.getenv("CLIENT_ID")
CHANNEL_ID = os.getenv("CHANNEL_ID")

HEADERS = {'Authorization': f'Bearer {AUTH_TOKEN}', 'Client-Id': CLIENT_ID}

def create_clip() -> str:
    url = f'{BASE_API}clips?broadcaster_id={CHANNEL_ID}'
    r = requests.post(url, headers=HEADERS)
    return_value = ""
    try:
        return_value = json.loads(r.text)["data"][0]["id"]
    except Exception as e:
        print(e)
    return return_value

def get_clip_url(clip_id: str) -> str:
    return_value = ""
    url = f'{BASE_API}clips?id={clip_id}'
    r = requests.get(url, headers=HEADERS)
    try:
        return_value = json.loads(r.text)["data"][0]["url"]
    except Exception as e:
        print(e)
    return return_value


def post_discord(message: str, link: str) -> str:
    header = {"Content-Type": "application/json"}
    data = json.dumps({
        "embeds":
        [
            {"title": message,
            "url": link
            }
        ]
    })
    r = requests.post(DISCORD_HOOK, data, headers = header)
    return r.text