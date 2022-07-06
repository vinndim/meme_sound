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


bot.run(TOKEN)
