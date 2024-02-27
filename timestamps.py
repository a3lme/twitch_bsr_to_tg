"""Parse """

from datetime import datetime
import re
import os
import sys
import asyncio

from aiogram import Bot
from dotenv import dotenv_values


config = {
    **dotenv_values(".env"),
    **os.environ,
}

bot = Bot(token=config["TG_BOT_TOKEN"])


async def main():
    """Parse files"""
    log_file = open(config["LOG_FILENAME"], "r", encoding="utf-8")
    lines = log_file.readlines()
    log_file.close()

    temp_file = open(config["TEMP_FILENAME"], "r", encoding="utf-8")
    message_text = temp_file.read()
    temp_file.close()

    start_time = await get_start_time(lines)

    start_song_regex = r"([0-9a-fA-F]+) / [0-9a-fA-F]+ \d+% \(bsr [0-9a-fA-F]+\) requested by @([a-zA-Z0-9_]+) is next!"

    for line in lines:

        m2 = re.search(start_song_regex, line)
        if m2:
            timestamp = line.split("|")[0]
            song_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            time_diff = song_time - start_time
            td_str = str(time_diff)
            x = td_str.split(":")
            replace_string = "#repl" + m2.group(1) + "*" + m2.group(2) + "#"
            message_text = message_text.replace(
                replace_string,
                f"<a href='{link}{x[0]}h{x[1]}m{x[2]}s'>{x[0]}:{x[1]}:{x[2]}</a>",
                1,
            )

    # print(message_text)
    await bot.send_message(config["TG_CHAT_ID"], message_text, parse_mode="HTML")


async def get_start_time(lines):
    """Find start stream message and return it's timestamp"""
    for line in lines:
        m = re.search(config["TWITCH_START_MESSAGE"], line)
        if m:
            timestamp = line.split("|")[0]
            return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")


if len(sys.argv) < 2:
    print("Requires link to stream as first argument.")
    exit()
link = sys.argv[1] + "?t="

asyncio.get_event_loop().run_until_complete(main())
