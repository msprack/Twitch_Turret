#!/usr/bin/env python3

from dotenv import load_dotenv
import os
import socket
import ssl
import asyncio
from gun import Gun

load_dotenv()
user = os.getenv("IRC_USER")
channel = os.getenv("CHANNEL_NAME")
OAUTH = os.getenv("IRC_AUTh")
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
                self.writer.write(f"PASS {OAUTH}\n".encode())
                await self.writer.drain()
                self.writer.write(f"NICK {user}\n".encode())
                await self.writer.drain()
                self.writer.write(f"JOIN {channel}\n".encode())
                await self.writer.drain()
            except Exception as e:
                print(e)
                continue
            break
    async def receive(self):
        while True:
            print("IRC Receiving")
            try:
                message = await self.reader.readline()
                message = message.decode()
                if "!ammo" in message:
                    await self.send_message(f"The dart turret has {self.gunner.rounds} rounds remaining.")
                if message:
                    print(message)
            except Exception as e:
                print(f"In receiving irc: {e}")
                pass
    async def send_message(self, message):
        self.writer.write(f"PRIVMSG {channel} :{message}\n".encode())
        await self.writer.drain()
    async def heartbeat(self):
        while True:
            print("beating irc")
            self.secure_socket.send(b"PONG :tmi.twitch.tv")
            await asyncio.sleep(60)
    def cleanup(self):
        pass
