#!/usr/bin/env python3

from dotenv import load_dotenv
import os
import socket
import ssl
import asyncio
from gun import Gun

TEST = False
load_dotenv()
user = os.getenv("IRC_USER")
channel = os.getenv("CHANNEL_NAME")
OAUTH = os.getenv("IRC_AUTH")
hostname = "irc.chat.twitch.tv"
port = 6697
context = ssl.create_default_context()

class IRC:
    def __init__(self, gunner: Gun):
        self.gunner = gunner
    async def connect(self):
        wait = 1
        while True:
            try:
                self.reader, self.writer = await asyncio.open_connection(hostname, port, ssl=context)
            except ConnectionError:
                asyncio.sleep(wait)
                wait *= 2
                print(f"Could not connect, increasing wait to {wait} and trying again.")
                continue
            try:
                self.writer.write(f"PASS {OAUTH}\n".encode())
                self.writer.write(f"NICK {user}\n".encode())
                await self.writer.drain()
                self.writer.write(f"JOIN {channel}\n".encode())
                await self.writer.drain()
            except ConnectionError as e:
                print("Connection errored out, got the following exception:")
                print(e)
                continue
            break
    async def receive(self):
        while True:
            try:
                message = await self.reader.readline()
                message = message.decode()
                if "PING :tmi.twitch.tv" in message:
                    self.writer.write(b"PONG :tmi.twitch.tv\n")
                    await self.writer.drain()
                if "!ammo" in message:
                    self.send_message(f"The dart turret has {self.gunner.rounds} rounds remaining.")
                if message:
                    print(message)
            except ConnectionError as e:
                print(f"In receiving irc: {e}")
                self.connect()
    def send_message(self, message):
        if not TEST:
            try:
                self.writer.write(f"PRIVMSG {channel} :{message}\n".encode())
                asyncio.create_task(self.writer.drain())
            except ConnectionError as e:
                print("In irc send_message, connection errored out, got the following exception:")
                print(e)
        else:
            print(message)
    def cleanup(self):
        pass
