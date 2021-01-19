#! /usr/bin/env python3

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
            return self.connection

    def generate_nonce(self):
        '''Generate pseudo-random number and seconds since epoch (UTC).'''
        nonce = uuid.uuid1()
        oauth_nonce = nonce.hex
        return oauth_nonce

    async def sendMessage(self, message):
        '''Sending message to webSocket server'''
        await self.connection.send(message)

    async def receiveMessage(self, connection):
        '''Receiving all server messages and handling them'''
        while True:
            try:
                print("awaiting websocket")
                message = await connection.recv()
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

    async def heartbeat(self, connection):
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
                await connection.send(json_request)
                await asyncio.sleep(60)
            except websockets.exceptions.ConnectionClosed:
                print('Connection with server closed')
    
    async def process_events(self, dictionary):
        if "message" in dictionary:
            message = json.loads(dictionary.get("message"))
            print(message)
        if dictionary.get("topic") == KITTENS:
            if message["type"] == "reward-redeemed":
                if message["data"]["redemption"]["reward"]["id"] == FIRE_EVENT_ID:
                    user = message["data"]["redemption"]["user"]["display_name"]
                    print("kittens")
                    self.kittens(user)
        elif dictionary.get("topic") == BITS:
            bit_data = message["data"]
            user = bit_data["user_name"]
            chat_message = bit_data["chat_message"]
            number_of_bits = bit_data["bits_used"]
            if FIRE_COMMAND.lower() in chat_message.lower():
                self.bits(user, number_of_bits)

    def kittens(self, user):
        # TODO: Kittens gambling portion
        # TODO: Only fire if the gun has ammo
        # print firing
        print("Test in kittens")
        loop = asyncio.get_running_loop()
        loop.create_task(self.fire(user, 3))



    def bits(self, user, number_of_bits):
        #TODO: Bits gambling portion
        loop = asyncio.get_running_loop()
        loop.create_task(self.fire(user, 3))

    async def fire(self, user, rounds):
        if self.gunner.rounds > 0:
            print(f'Firing {rounds} rounds')
            await self.irc.send_message(f'Firing {rounds} rounds')
            self.gunner.fire(rounds)
            await self.irc.send_message(f"{rounds} have been fired, {self.gunner.rounds} remaining.")
            # Wait 20 seconds
            await asyncio.sleep(20)
            print("Slept for 20 seconds")
            # create a clip
            clip_id = create_clip()
            print(clip_id)
            # Wait fifteen seconds
            await asyncio.sleep(15)
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
        else:
            self.irc.send
    def cleanup(self):
        self.gunner.cleanup()
        self.irc.cleanup()
    
