# Twitch BSR parser

This project created for easy make song list with timestamp after streams of BeatSaber.

# Quick run without docker

- Create python virtual environment `python3 -m venv env`
- Activate vitrual environment `source env/bin/activate`
- Install projetc dependencies `python3 -m pip install -r requirements.txt`
- Create `.env` file with variables:

```
TWITCH_OAUTH=<twitch_oauth_token>
TWITCH_OAUTH_NICKNAME=<twitch_username_for_oauth_token>
TWITCH_CHANNEL=<twitch_channel_name>
TWITCH_START_MESSAGE=<message_text_for_start_stream>
TWITCH_END_QUEUE_MESSAGE=<message_text_for_end_bsr_queue>
TG_BOT_TOKEN=<telegram_token>
TG_CHAT_ID=<telegram_chat_id>
LOG_FILENAME="log.txt"
TEMP_FILENAME="temp.txt"
DEBUG=0#Optional, for read messages from TEST_FILENAME
TEST_FILENAME="test_log.txt"
```

- Run main `python3 main.py`
- After end queue bot sends message to chat with list of songs. Don't shutdown bot.
- After end of stream stop bot and run timestamps `python3 timestamps.py <link_to_stream>`.
  Link to stream must be without any timestamps. It will sends new message to chat, with song list and timestamps.

# Quick run with docker

- Create `.env` file with variables:

```
TWITCH_OAUTH=<twitch_oauth_token>
TWITCH_OAUTH_NICKNAME=<twitch_username_for_oauth_token>
TWITCH_CHANNEL=<twitch_channel_name>
TWITCH_START_MESSAGE=<message_text_for_start_stream>
TWITCH_END_QUEUE_MESSAGE=<message_text_for_end_bsr_queue>
TG_BOT_TOKEN=<telegram_token>
TG_CHAT_ID=<telegram_chat_id>
LOG_FILENAME="log/log.txt"
TEMP_FILENAME="log/temp.txt"
DEBUG=0#Optional, for read messages from TEST_FILENAME
TEST_FILENAME="test_log.txt"
```

- Run docker at stage `runner`, mount /app/log as docker volume
- After steram run docker at stage `timestamps`, mount /app/log as docker volume
