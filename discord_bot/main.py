import discord
from discord.ext import commands
from config import TOKEN, FFMPEG_OPTIONS
from parsing import YTDLSource
from text_song import get_lyric

bot = commands.Bot(command_prefix='!')


class MemeSound(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.url = ""
        self.title = ''
        self.playlist = []

    @commands.command(name="connect")
    async def join_voice(self, ctx):
        connected = ctx.author.voice
        if connected:
            await connected.channel.connect()
        else:
            await ctx.send("Зайди в голосвой чат")

    @commands.command(name='leave', help='To make the bot leave the voice channel')
    async def leave(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_connected():
            await voice_client.disconnect()
        else:
            await ctx.send("Я не в голосовом чате")

    @commands.command(name='100-7', help='To play song')
    async def play(self, ctx, url):
        await self.join_voice(ctx)
        server = ctx.message.guild
        voice_channel = server.voice_client
        voice_client = ctx.message.guild.voice_client
        if not voice_client.is_playing():
            filename, self.title = await YTDLSource.from_url(url, loop=bot.loop)
            voice_channel.play(discord.FFmpegPCMAudio(executable="C:\\ffmpeg\\bin\\ffmpeg.exe",
                                                      source=filename, **FFMPEG_OPTIONS))
            async with ctx.typing():
                await ctx.send(f'**Now playing:** {self.title}')

    @commands.command(name='pause', help='This command pauses the song')
    async def pause(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await voice_client.pause()
            await voice_client.send('')
        else:
            await ctx.send("Музыку добавь, дурачёк!")

    @commands.command(name='resume', help='Resumes the song')
    async def resume(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            await voice_client.resume()
        else:
            await ctx.send("Музыку добавь, дурачёк!")

    @commands.command(name='stop', help='Stops the song')
    async def stop(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await voice_client.stop()
        else:
            await ctx.send("Где музыка?")

    @commands.command(name='text', help='Stops the song')
    async def text(self, ctx):
        async with ctx.typing():
            await ctx.send(get_lyric(self.title))


if __name__ == '__main__':
    bot.add_cog(MemeSound(bot))
    bot.run(TOKEN)
