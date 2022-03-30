import discord
from discord.ext import commands

from config import TOKEN

bot = commands.Bot(command_prefix="!")


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    print("Bot start working...")
    bot.load_extension('music')


bot.run(TOKEN)
