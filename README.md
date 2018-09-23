# Pick-Bot

## Setup
Requires `discord.py` and `ruamel.yaml` python packages.

Run `python main.py` to start the bot.

### Commands

#### /lotto start #channel :emote:
Sends the `start` embed from the config to the specified channel and adds the given reaction.

#### /lotto end #channel message_id count
Selects `count` members that reacted to the specified channel message and sends the `end` embed to the channel.

#### /lotto who #channel message_id
Displays the number of users who have reacted to the given message, and randomly displays 10 of those users.


Still WIP, but I'm calling it a night.
Code so far: https://github.com/TeamDman/Pick-Bot
