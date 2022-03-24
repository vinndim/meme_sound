import discord
from discord.ext import commands

from discord_bot.code.config import TOKEN

bot = commands.Bot(command_prefix="!")


@bot.event
async def on_ready():
    print(f'{bot.user} has logged in.')
    bot.load_extension('main_bot')


bot.run(TOKEN)
# 2022-03-24 15:04:05.373  WARN 13220 --- [kground-preinit] o.s.h.c.j.Jackson2ObjectMapperBuilder    : For Jackson Kotlin classes support please add "com.fasterxml.jackson.module:jackson-module-kotlin" to the classpath
# 2022-03-24 15:04:05.395 ERROR 13220 --- [           main] lavalink.server.Launcher                 : Application failed
#
# java.lang.UnsupportedClassVersionError: lavalink/server/info/AppInfo has been compiled by a more recent version of the Java Runtime (class file version 55.0), this version of the Java Runtime only recognizes class file versions up to 5
# 2.0
