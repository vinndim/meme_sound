from discord.ext import commands

from config import TOKEN

bot = commands.Bot(command_prefix='!')


@bot.command(name="connect")
async def join_voice(ctx):
    connected = ctx.author.voice
    if connected:
        await connected.channel.connect()  # Use the channel instance you put into a variable
    else:
        await ctx.send("Зайди в голосвой чат, утырок")


if __name__ == '__main__':
    bot.run(TOKEN)

# I'm beginning to think they have very similar qualities and can do the same things but is a personal preference to go with a client vs. a bot.
# However they do have their differences where clients have an on_message while bots wait for a prefix command.
