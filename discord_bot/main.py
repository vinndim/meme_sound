import discord
import yt_dlp
from discord import Client

from discord.ext import commands

from config import TOKEN
from discord_bot.user_info import get_info
from yt_video import YTDLSource
from text_song import get_lyric


class MemeSound(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.title = ""

    @commands.command("connect")
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command(name='100-7', help='To play song')
    async def stream(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
            self.title = player.title

        await ctx.send(f'**Now playing**: {player.title}')

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    @commands.command("stop")
    async def stop(self, ctx):
        await ctx.voice_client.disconnect()

    @stream.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

    @commands.command(name='text', help='Stops the song')
    async def text(self, ctx):
        async with ctx.typing():
            if self.title:
                await ctx.send(f'{await get_lyric(self.title)}')
            else:
                await ctx.send("Нет названия песни")

    @commands.command("info")
    async def info(self, ctx, member: discord.Member = None, guild: discord.Guild = None):
        async with ctx.typing():
            await get_info(ctx, member, guild)


bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"))


@bot.command(name="passwd")
async def send_msg(ctx):
    user_id = int(ctx.message.author.id)
    user_chat = await bot.fetch_user(user_id)
    print(user_chat)
    await user_chat.send('**Ваш пароль:**')


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


if __name__ == '__main__':
    bot.add_cog(MemeSound(bot))
    if TOKEN:
        print('<<token received>>')
        print("Bot start working...")
        bot.run(TOKEN)
    else:
        print("<<token is none>>")
