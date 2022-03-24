import discord
from discord.ext import commands

from config import TOKEN

bot = commands.Bot(command_prefix="!")


@bot.event
async def on_ready():
    print(f'{bot.user} has logged in.')
    bot.load_extension('music')


bot.run(TOKEN)
