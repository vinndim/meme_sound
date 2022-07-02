from discord.ext import commands
from discord_components import DiscordComponents

from dotenv import load_dotenv
import os

env_path = "token.env"
load_dotenv(dotenv_path=env_path)
TOKEN = os.getenv("TOKEN")
print(TOKEN)


def get_prefix(bot, message):
    prefixes = ['-', '!']
    if not message.guild:
        # Only allow ? to be used in DMs
        return '?'
    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, message)


bot = commands.Bot(command_prefix=get_prefix)

# дополнение к discord.py (кнопки)
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
    if before.channel is not None and after.channel is None:
        # Бот выходит, если остаётся один в голосовом чате
        if len(before.channel.members) == 1 and before.channel.members[0].id == bot.user.id:
            guild_id = before.channel.members[0].guild.id
            ws = bot._connection._get_websocket(guild_id)
            await ws.voice_state(str(guild_id), None)


bot.run(TOKEN)
