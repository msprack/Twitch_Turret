#! /usr/bin/env python3

from time import sleep
from math import ceil
import random
from dotenv import load_dotenv
import os
from webClient import *
import websockets
import asyncio
import uuid
import json
import logging
from irc import IRC
from gun import Gun
#logging.basicConfig(level=logging.DEBUG)
load_dotenv()
AUTH_TOKEN = os.getenv("OAUTH")
KITTENS = "channel-points-channel-v1.108914265"
BITS = "channel-bits-events-v2.108914265"
FIRE_EVENT_ID = os.getenv("REDEMPTION_ID")
FIRE_COMMAND = "!fire"
class WebSocketClient():
    def __init__(self):
        # list of topics to subscribe to
        self.topics = [KITTENS, BITS]
        self.gunner = Gun()
        self.irc = IRC(self.gunner)
    async def connect(self):
        '''
           Connecting to webSocket server
           websockets.client.connect returns a WebSocketClientProtocol, which is used to send and receive messages
        '''
        self.connection = await websockets.client.connect('wss://pubsub-edge.twitch.tv')
        if self.connection.open:
            print('Connection established. Client correctly connected')
            # Send greeting
            message = {"type": "LISTEN", "nonce": str(self.generate_nonce()), "data":{"topics": self.topics, "auth_token": AUTH_TOKEN}}
            json_message = json.dumps(message)
            await self.sendMessage(json_message)

    def generate_nonce(self):
        '''Generate pseudo-random number and seconds since epoch (UTC).'''
        nonce = uuid.uuid1()
        oauth_nonce = nonce.hex
        return oauth_nonce

    async def sendMessage(self, message):
        '''Sending message to webSocket server'''
        await self.connection.send(message)

    async def receiveMessage(self):
        '''Receiving all server messages and handling them'''
        while True:
            try:
                print("awaiting websocket")
                message = await self.connection.recv()
                print('Received message from server: ' + str(message))
                dictionary = json.loads(message)
                if "data" in dictionary:
                    await self.process_events(dictionary["data"])
                pass
            except websockets.exceptions.ConnectionClosed:
                print('Connection with server closed')
                break
            except ValueError as e:
                print("Error Parsing JSON")
                print(e)

    async def heartbeat(self):
        '''
        Sending heartbeat to server every 1 minutes
        Ping - pong messages to verify/keep connection is alive
        '''
        while True:
            print("beating")
            try:
                data_set = {"type": "PING"}
                json_request = json.dumps(data_set)
                print(json_request)
                await self.connection.send(json_request)
                await asyncio.sleep(60)
            except websockets.exceptions.ConnectionClosed:
                self.connect()
    
    async def process_events(self, dictionary):
        if "message" in dictionary:
            message = json.loads(dictionary.get("message"))
            print(message)
        if dictionary.get("topic") == KITTENS:
            if message["type"] == "reward-redeemed":
                if message["data"]["redemption"]["reward"]["id"] == FIRE_EVENT_ID:
                    user = message["data"]["redemption"]["user"]["display_name"]
                    print("kittens")
                    l = asyncio.create_task(self.kittens(user))
        elif dictionary.get("topic") == BITS:
            bit_data = message["data"]
            user = bit_data["user_name"]
            chat_message = bit_data["chat_message"]
            number_of_bits = bit_data["bits_used"]
            asyncio.create_task(self.bits(user, number_of_bits))

    async def kittens(self, user):
        # The prelude
        self.irc.send_message(f"@{user} sacrificed a bag of kittens to the cannon gods.")
        # Check for ammo
        if self.gunner.rounds > 0:
            # Kittens have a one in 40 chance of firing
            if random.randint(1, 40) == 1:
                self.irc.send_message(f"The gods purr fondly at the devotion of @{user} and unleash the cannon.")
                # Kitten redemptions can only fire 3 rounds
                await self.fire(user, 3)
            # Send a failure message
            else:
                self.irc.send_message(f"The gods have smote @{user} for their arrogance")
        # Send a failure message if there is no ammo.
        else:
            self.irc.send_message("The gunner is out of ammo. Always use the !ammo command before attempting to fire.")


    async def bits(self, user, number_of_bits):
        # The prelude
        self.irc.send_message(f"@{user} hands {number_of_bits} drachmas to the gatekeeper and steps into the dragon's lair.")
        if number_of_bits < 100:
            self.irc.send_message(f"The gatekeeper shakes his head at you and sends you away. You must pay at least 100 drachmas to enter the lair.")
            return
        # Check for ammo
        if self.gunner.rounds > 0:
            dollars = number_of_bits / 100 + 2
            # More dollars, better odds
            r = random.randint(1, max(2, 100//dollars))
            print(r)
            if r == 1:
                try:
                    # More dollars, more rounds fired. Up to half of the dollars gambled plus 3
                    rounds = 3 + ceil(random.randint(0, dollars)/2)
                    # Send a success message
                    self.irc.send_message(f"@{user} unleashes a hail of gunfire, striking the Red Dragon with {rounds} rounds.")
                    # Only up to ten rounds can be fired though
                    await self.fire(user, min(10, rounds))
                except Exception as e:
                    print(e)
            # Pithy failure message
            else:
                self.irc.send_message(f"@{user} tried to fire their weapon at the Red Dragon but was struck down mercilessly")
        # Remind users to check ammo before gambling
        else:
            self.irc.send_message("The gunner is out of ammo. Always use the !ammo command before attempting to fire.")

    async def fire(self, user, rounds):
        if self.gunner.rounds > 0:
            print(f'Firing {rounds} rounds')
            self.gunner.fire(rounds)
            self.irc.send_message(f"{rounds} have been fired, {self.gunner.rounds} remaining.")
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
                self.irc.send_message(f'This firing event has been clipped, check it out on discord.')
            print("End of firing.")
    def cleanup(self):
        self.gunner.cleanup()
        self.irc.cleanup()
    
