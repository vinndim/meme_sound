from discord.ext import commands

from support_code.config import TOKEN
from discord_components import DiscordComponents

bot = commands.Bot(command_prefix="!")
DiscordComponents(bot)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    print("Bot start working...")
    bot.remove_command("help")
    cogs = ["discord_bot.cogs.music_cog", "discord_bot.cogs.support_cog"]
    for cog in cogs:
        bot.load_extension(cog)


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
