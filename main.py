"""Twitch chat logger"""

import asyncio
from datetime import datetime
import io
import os
import re
from signal import SIGINT, SIGTERM
from aiogram import Bot
import websockets
import requests
from dotenv import dotenv_values


config = {
    **dotenv_values(".env"),
    **os.environ,
}

bot = Bot(token=config["TG_BOT_TOKEN"])


async def main():
    """Main function for connecting to chat and processing messages."""
    async for websocket in websockets.connect("ws://irc-ws.chat.twitch.tv:80"):
        try:
            await websocket.send(
                "CAP REQ :twitch.tv/membership twitch.tv/tags twitch.tv/commands"
            )
            await websocket.send(f"PASS oauth:{config['TWITCH_OAUTH']}")
            await websocket.send(f"NICK {config['TWITCH_OAUTH_NICKNAME']}")
            await websocket.send(f"JOIN #{config['TWITCH_CHANNEL']}")
            while True:
                message = await websocket.recv()
                if "PING :tmi.twitch.tv" in message:
                    await websocket.send("PONG :tmi.twitch.tv")
                else:
                    await message_processing(message)
        except websockets.ConnectionClosed:
            continue
        except asyncio.CancelledError:
            await websocket.close()
            return


async def test():
    """Test function that read messages from log"""
    test_file = open(
        config["TEST_FILENAME"],
        "r",
        encoding="utf-8",
    )
    lines = test_file.readlines()
    for line in lines:
        await message_processing(line)


def get_log_file() -> io.TextIOWrapper:
    """Get file for logging messages. If file is not open or it's time to change file, it will be created or changed."""
    log_file = open(
        config["LOG_FILENAME"],
        "a",
        encoding="utf-8",
    )
    return log_file


def get_temp_file() -> io.TextIOWrapper:
    """Get file for logging messages. If file is not open or it's time to change file, it will be created or changed."""
    temp_file = open(
        config["TEMP_FILENAME"],
        "a",
        encoding="utf-8",
    )
    return temp_file


async def message_processing(msg: str) -> None:
    """Process message from chat and write it to file."""
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "|" + msg)
    if (
        (
            f" :{config['TWITCH_CHANNEL']}!{config['TWITCH_CHANNEL']}@{config['TWITCH_CHANNEL']}.tmi.twitch.tv "
            in msg
        )
        or ":!bsr " in msg
        or config["TWITCH_START_MESSAGE"] in msg
    ):
        # Save message to main log
        get_log_file().write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "|" + msg)
        # Parse request
        add_song_regex = r"\(bsr [0-9a-fA-F]+\) ([0-9a-fA-F]+) / [0-9a-fA-F]+ \d+% requested by @([a-zA-Z0-9_]+) added to queue."
        m = re.search(add_song_regex, msg)
        if m:
            r = requests.get(
                "https://beatsaver.com/api/maps/id/" + m.group(1), timeout=10
            )
            song = r.json()
            get_temp_file().write(
                f"#repl{m.group(1)}*{m.group(2).lower()}# - "
                + song["name"]
                + " //"
                + '<a href="https://beatsaver.com/maps/'
                + m.group(1)
                + '">'
                + m.group(1)
                + "</a> by "
                + m.group(2)
                + "\n"
            )
    if config["TWITCH_END_QUEUE_MESSAGE"] in msg:
        temp = open(
            config["TEMP_FILENAME"],
            "r",
            encoding="utf-8",
        )
        lines = temp.readlines()
        temp.close()
        message = ""
        for line in lines:
            remove_timestamp_regex = r"(#repl[0-9a-fA-F]+\*[a-z0-9_]+# - )(.*)$"
            m2 = re.search(remove_timestamp_regex, line)
            if m2:
                message += m2.group(2) + "\n"
        if message:
            await bot.send_message(config["TG_CHAT_ID"], message, parse_mode="HTML")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    if config["DEBUG"]:
        main_task = asyncio.ensure_future(test())
    else:
        main_task = asyncio.ensure_future(main())
    for signal in [SIGINT, SIGTERM]:
        loop.add_signal_handler(signal, main_task.cancel)
    try:
        loop.run_until_complete(main_task)
    finally:
        loop.close()
