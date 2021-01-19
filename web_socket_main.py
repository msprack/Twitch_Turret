#!/usr/bin/env python3
import asyncio
from webSocketClient import WebSocketClient

if __name__ == '__main__':
    try:
        # Creating client object
        client = WebSocketClient()
        # Access the event loop for async scheduling
        loop = asyncio.get_event_loop()
        print(loop.is_running())
        # Start connection and get client connection protocol
        loop.run_until_complete(client.irc.connect())
        connection = loop.run_until_complete(client.connect())
        # Start listener and heartbeat
        tasks = [
            asyncio.ensure_future(client.irc.receive()),
            asyncio.ensure_future(client.irc.heartbeat()),
            asyncio.ensure_future(client.heartbeat(connection)),
            asyncio.ensure_future(client.receiveMessage(connection)),
        ]
        print("Starting")
        loop.run_until_complete(asyncio.wait(tasks))
    except KeyboardInterrupt:
        client.cleanup()