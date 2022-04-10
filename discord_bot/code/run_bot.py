from discord.ext import commands

from config import TOKEN
from discord_components import DiscordComponents
from music import Music, stop

bot = commands.Bot(command_prefix="!")
DiscordComponents(bot)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    print("Bot start working...")
    bot.load_extension("music")


@bot.event
async def on_voice_state_update(member, before, after):
    try:
        if len(before.channel.members) == 0:
            await stop(member, before.channel)
    except AttributeError:
        pass
    if before.channel is None and after.channel is not None:
        print(f'Пользователь {member} зашёл в канал {after.channel}, в канале {len(after.channel.members)}')
    elif before.channel is not None and after.channel is None:
        print(f'Пользователь {member} вышел из канала {before.channel}, в канале {len(before.channel.members)}')


bot.run(TOKEN)
