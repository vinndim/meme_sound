import os
# lavalink/server/info/AppInfo has been compiled by a more recent version of the Java Runtime (class file version 55.0),
# this version of the Java Runtime only recognizes class file versions up to 52.0
import discord
from discord.ext import commands
import lavalink
from discord import utils
from discord import Embed


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.music = lavalink.Client(self.bot.user.id)
        self.bot.music.add_node('localhost', 7000, 'testing', 'na', 'music-node')
        self.bot.add_listener(self.bot.music.voice_update_handler, 'on_socket_response')
        self.bot.music.add_event_hook(self.track_hook)

    @commands.command(name='play')
    async def play(self, ctx, *, query):
        try:
            player = self.bot.music.player_manager.get(ctx.guild.id)
            query = f'ytsearch:{query}'
            results = await player.node.get_tracks(query)
            tracks = results['tracks'][0:10]
            i = 0
            query_result = ''
            for track in tracks:
                i = i + 1
                query_result = query_result + f'{i}) {track["info"]["title"]} - {track["info"]["uri"]}\n'
            embed = Embed()
            embed.description = query_result

            await ctx.channel.send(embed=embed)

            def check(m):
                return m.author.id == ctx.author.id

            response = await self.bot.wait_for('message', check=check)
            track = tracks[int(response.content) - 1]

            player.add(requester=ctx.author.id, track=track)
            if not player.is_playing:
                await player.play()

        except Exception as error:
            print(error)

    @commands.command(name='skip', aliases=['forceskip', 'fs', 'next'])
    async def skip(self, ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Not playing anything :mute:')

        await ctx.send('⏭ | Skipped.')
        await player.skip()

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
