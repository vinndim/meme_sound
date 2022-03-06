from discord.ext import commands

from config import TOKEN

bot = commands.Bot(command_prefix='!')


@bot.command(name="connect")
async def join_voice(ctx):
    connected = ctx.author.voice
    if connected:
        await connected.channel.connect()
    else:
        await ctx.send("Зайди в голосвой чат, утырок")


if __name__ == '__main__':
    bot.run(TOKEN)
