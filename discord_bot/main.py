import discord
from discord.ext import commands
from config import TOKEN, FFMPEG_OPTIONS
from parsing import YTDLSource

bot = commands.Bot(command_prefix='!')


@bot.command(name="connect")
async def join_voice(ctx):
    connected = ctx.author.voice
    if connected:
        await connected.channel.connect()
    else:
        await ctx.send("Зайди в голосвой чат, утырок")


@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("Я не в голосовом чате, критин")


playlist = []


@bot.command(name='100-7', help='To play song')
async def play(ctx, url):
    await join_voice(ctx)
    server = ctx.message.guild
    voice_channel = server.voice_client
    voice_client = ctx.message.guild.voice_client
    if not voice_client.is_playing():
        filename, title = await YTDLSource.from_url(url, loop=bot.loop)
        voice_channel.play(discord.FFmpegPCMAudio(executable="C:\\ffmpeg\\bin\\ffmpeg.exe",
                                                  source=filename, **FFMPEG_OPTIONS))
        async with ctx.typing():
            await ctx.send(f'**Now playing:** {title}')


@bot.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
        await voice_client.send('')
    else:
        await ctx.send("Музыку добавь, дурачёк!")


@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("Музыку добавь, дурачёк!")


@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("Где музыка, шиз?")


@bot.command(name='text', help='Stops the song')
async def text(ctx, artist, song):
    async with ctx.typing():
        text = await YTDLSource.get_text(artist, song)
        server = ctx.message.guild
        await ctx.send(text)


if __name__ == '__main__':
    bot.run(TOKEN)
