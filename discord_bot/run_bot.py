from discord.ext import commands
from discord_components import DiscordComponents

from dotenv import load_dotenv
import os

env_path = "token.env"
load_dotenv(dotenv_path=env_path)
TOKEN = os.getenv("TOKEN")
print(TOKEN)


def get_prefix(bot, message):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""

    # Notice how you can use spaces in prefixes. Try to keep them simple though.
    prefixes = ['-', '!']

    # Check to see if we are outside of a guild. e.g DM's etc.
    if not message.guild:
        # Only allow ? to be used in DMs
        return '?'

    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, message)


bot = commands.Bot(command_prefix=get_prefix)

# дополнение к discord.py
DiscordComponents(bot)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    print("Bot start working...")
    bot.remove_command("help")
    cogs = ["discord_bot.cogs.music_cog", "discord_bot.cogs.help_cog"]
    for cog in cogs:
        bot.load_extension(cog)


# отслеживание выхода и входа пользователей
@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        print(f'Пользователь {member} зашёл в канал {after.channel}, в канале {len(after.channel.members)}')
    elif before.channel is not None and after.channel is None:
        print(f'Пользователь {member} вышел из канала {before.channel}, в канале {len(before.channel.members)}')
        # Бот выходит, если остаётся один в голосовом чате
        if len(before.channel.members) == 1 and before.channel.members[0].id == bot.user.id:
            guild_id = before.channel.members[0].guild.id
            ws = bot._connection._get_websocket(guild_id)
            await ws.voice_state(str(guild_id), None)

bot.run(TOKEN)
