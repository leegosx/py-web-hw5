# pyW-m5-hw

# Simple WebSocket Chat Application

Hello! This is a simple web chat application developed using Python (aiohttp, asyncio) for the server-side and JavaScript (WebSocket) for the client-side.

## Description

This web chat allows users to exchange real-time messages through WebSocket. The chat features the following functionalities:

- Sending and receiving text messages
- `exchange <days>` command to retrieve currency exchange rates for the last few days
- Logging of the `exchange` command to a file

## How to Use

1. Clone this repository to your computer.
2. Make sure you have Python and the aiohttp library installed (`pip install aiohttp`).
3. Open a terminal and navigate to the project folder.
4. Start the server by running: `python ws-server.py`.
5. Open the `index.html` file in your browser.

## Chat Commands

- To send a regular message, simply start typing and press Enter.
- To retrieve currency exchange rates for the last few days, send the `exchange <days>` command, where `<days>` is the number of days.
- Example: `exchange 3` - retrieve currency exchange rates for the last 3 days.

## Logging

The `exchange` commands are logged to the `exchange_log.txt` file, which is located in the project's root folder.

## Note

This is a demonstration project and can be customized and expanded according to your needs. Please note that this chat does not provide authentication and security, so avoid using it for transmitting confidential information.

