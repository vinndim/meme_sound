import math
import os
# lavalink/server/info/AppInfo has been compiled by a more recent version of the Java Runtime (class file version 55.0),
# this version of the Java Runtime only recognizes class file versions up to 52.0
import discord
from discord.ext import commands
import lavalink
from discord import utils
from discord import Embed

from discord_bot.code.text_song import get_lyric


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.music = lavalink.Client(self.bot.user.id)
        self.bot.music.add_node('localhost', 7000, 'testing', 'na', 'music-node')
        self.bot.add_listener(self.bot.music.voice_update_handler, 'on_socket_response')
        self.bot.music.add_event_hook(self.track_hook)
        self.title = ""

    @commands.command(name='play', aliases=['p', 'sing'])
    async def play(self, ctx, *, query):
        player = self.bot.music.player_manager.get(ctx.guild.id)

        query = query.strip('<>')

        if not query.startswith('http'):
            query = f'ytsearch:{query}'

        results = await player.node.get_tracks(query)

        if not results or not results['tracks']:
            return await ctx.send('Song not found :x: Please try again :mag_right:')

        em = discord.Embed(colour=discord.Colour(0xFF69B4))

        if results['loadType'] == 'PLAYLIST_LOADED':
            tracks = results['tracks']

            for track in tracks:
                # Add all of the tracks from the playlist to the queue.
                player.add(requester=ctx.author.id, track=track)

            em.title = 'Playlist Enqueued!'
            em.description = f'{results["playlistInfo"]["name"]} - {len(tracks)} tracks'
        else:
            track = results['tracks'][0]
            em.title = 'Track Enqueued'
            em.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'
            em.set_thumbnail(url=f"http://i.ytimg.com/vi/{track['info']['identifier']}/hqdefault.jpg")

            em.add_field(name='Channel', value=track['info']['author'])
            if track['info']['isStream']:
                duration = 'Live'
            else:
                duration = lavalink.format_time(track['info']['length']).lstrip('00:')
            em.add_field(name='Duration', value=duration)
            self.title = track["info"]["title"]
            track = lavalink.models.AudioTrack(track, ctx.author.id, recommended=True)
            player.add(requester=ctx.author.id, track=track)

        if not player.is_playing:
            await player.play()
            await player.reset_equalizer()
            # send nice msg
            await ctx.send(embed=em)
            # await self.now(ctx)

    @commands.command(name='queue', aliases=['q', 'playlist'])
    async def queue(self, ctx, page: int = 0):
        player = self.bot.music.player_manager.get(ctx.guild.id)

        if not player.queue:
            return await ctx.send('Нет песен :cd:')

        items_per_page = 10
        pages = math.ceil(len(player.queue) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue_list = ''

        for i, track in enumerate(player.queue[start:end], start=start):
            queue_list += f'`{i + 1}.` [**{track.title}**]({track.uri})\n'

        embed = discord.Embed(colour=discord.Colour(0xFF69B4),
                              description=f'**{len(player.queue)} tracks**\n\n{queue_list}')
        embed.set_footer(text=f'Viewing page {page}/{pages}')
        await ctx.send(embed=embed)

    @commands.command(name='skip', aliases=['forceskip', 'fs', 'next'])
    async def skip(self, ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Ничего не играет и да... :mute:')

        await ctx.send('⏭ | Skipped.')
        await player.skip()

    @commands.command(name='text', help='text song')
    async def text(self, ctx):
        async with ctx.typing():
            await ctx.send(await get_lyric(self.title))

    @play.before_invoke
    async def ensure_voice(self, ctx):
        print('join command worked')
        member = utils.find(lambda m: m.id == ctx.author.id, ctx.guild.members)
        if member is not None and member.voice is not None:
            vc = member.voice.channel
            player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
            if not player.is_connected:
                player.store('channel', ctx.channel.id)
                await self.connect_to(ctx.guild.id, str(vc.id))

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            await self.connect_to(guild_id, None)

    async def connect_to(self, guild_id: int, channel_id: str):
        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)


def setup(bot):
    bot.add_cog(Music(bot))