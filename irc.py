#!/usr/bin/env python3

from webClient import *
from math import ceil
import random
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
                await self.writer.drain()
                self.writer.write(f"NICK {user}\n".encode())
                print("nick and pass")
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
                if message.startswith(":streamlabs!streamlabs@streamlabs.tmi.twitch.tv"):
                    if "just donated" in message:
                        user = message.split()[3][1:]
                        dollars = float(message.split()[-1][1:-1])
                        self.send_message(f"@{user} hands {int(dollars * 100)} drachmas to the gatekeeper and steps into the dragon's lair.")
                        if  dollars < 100.0:
                            self.send_message(f"The gatekeeper shakes his head at you and sends you away. You must pay at least 100 drachmas to enter the layer.")
                            return
                        # Check for ammo
                        if self.gunner.rounds > 0:
                            dollars = dollars + 2
                            # More dollars, better odds
                            r = random.randint(1, max(2, 100//dollars))
                            print(r)
                            if r == 1:
                                try:
                                    # More dollars, more rounds fired. Up to half of the dollars gambled plus 3
                                    rounds = 3 + ceil(random.randint(0, dollars)/2)
                                    # Send a success message
                                    self.send_message(f"@{user} unleashes a hail of gunfire, striking the Red Dragon with {rounds} rounds.")
                                    # Only up to ten rounds can be fired though
                                    await self.fire(user, min(10, rounds))
                                except Exception as e:
                                    print(e)
                            # Pithy failure message
                            else:
                                self.send_message(f"@{user} tried to fire their weapon at the Red Dragon but was struck down mercilessly")
                        # Remind users to check ammo before gambling
                        else:
                            self.send_message("The gunner is out of ammo. Always use the !ammo command before attempting to fire.")
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

    async def fire(self, user, rounds):
        if self.gunner.rounds > 0:
            print(f'Firing {rounds} rounds')
            self.gunner.fire(rounds)
            self.send_message(f"{rounds} have been fired, {self.gunner.rounds} remaining.")
            # Wait 20 seconds
            asyncio.sleep(20)
            print("Slept for 20 seconds")
            # create a clip
            clip_id = create_clip()
            print(clip_id)
            # Wait fifteen seconds
            asyncio.sleep(15)
            print("slept for 15 seconds")
            # Get the clip url
            clip_url = get_clip_url(clip_id)
            print(clip_url)
            # If the url exists:
            if clip_url != "":
                # dump it into discord
                print(post_discord(f'Watch Red get blasted by {user}', clip_url))
                self.send_message(f'This firing event has been clipped, check it out on discord.')
            print("End of firing.")
