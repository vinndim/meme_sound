import math

import discord
from discord.ext import commands
import lavalink
from discord import utils

from discord_bot.code.text_song import get_lyric, get_normal_title


async def command_user(ctx, msg):
    em = discord.Embed(colour=ctx.message.author.color, title=f"Command by "
                                                              f"{ctx.message.author.display_name}  |  "
                                                              f"<{msg}>")
    await ctx.send(embed=em)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.music = lavalink.Client(self.bot.user.id)
        self.bot.music.add_node('localhost', 7000, 'testing', 'ru', 'music-node')
        self.bot.add_listener(self.bot.music.voice_update_handler, 'on_socket_response')
        self.bot.music.add_event_hook(self.track_hook)
        self.title = ""
        self.ctx = None

    @commands.command(name='play', aliases=['p', 'sing', '100-7'])
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
            self.ctx = ctx

        if not player.is_playing:
            await player.play()
        else:
            await ctx.send(embed=em)

    @commands.command(name='queue', aliases=['q', 'playlist'])
    async def queue(self, ctx, page: int = 1):
        await ctx.message.delete()
        await command_user(ctx, ctx.message.content)
        player = self.bot.music.player_manager.get(ctx.guild.id)

        if not player.queue:
            return await ctx.send('Queue empty! Why not queue something? :cd:')

        items_per_page = 10
        pages = math.ceil(len(player.queue) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue_list = ''

        for i, track in enumerate(player.queue[start:end], start=start):
            queue_list += f'`{i + 1}.` [**{track.title}**]({track.uri})\n'

        embed = discord.Embed(colour=discord.Colour(0xFF69B4),
                              description=f'**{len(player.queue)} tracks**\n\n{queue_list}')
        embed.set_footer(text=f'{page}/{pages}')
        await ctx.send(embed=embed)

    @commands.command(name='now', aliases=['np'])
    async def now(self, ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)

        if player.current:
            if player.current.stream:
                dur = 'LIVE'
                pos = ''
                count = total = 1
            else:
                count = player.position
                pos = lavalink.format_time(count)
                total = player.current.duration
                dur = lavalink.format_time(total)
                if pos == dur:  # When called immediatly after enqueue
                    count = 0
                    pos = '00:00:00'
                dur = dur.lstrip('00:')
                pos = pos[-len(dur):]
            bar_len = 30  # bar length
            filled_len = int(bar_len * count // float(total))
            bar = '═' * filled_len + '♫' + '─' * (bar_len - filled_len)
            song = f'[{get_normal_title(player.current.title)}]({player.current.uri})\n`{pos} {bar} {dur}`'

            em = discord.Embed(colour=discord.Colour(0xFF69B4), description=song)
            em.set_author(name="**Сейчас играет**",
                          icon_url="https://media.giphy.com/media/LIQKmZU1Jm1twCRYaQ/giphy.gif")
            em.set_thumbnail(url=f"http://i.ytimg.com/vi/{player.current.identifier}/hqdefault.jpg")

            await ctx.send(embed=em)
            await self.bot.change_presence(
                activity=discord.Activity(type=discord.ActivityType.listening,
                                          name=await get_normal_title(player.current.title)))
        else:
            await ctx.send('Ничего не играет :mute:')

    @commands.command(name='skip', aliases=['forceskip', 'fs', 'next'])
    async def skip(self, ctx):
        await ctx.message.delete()
        await command_user(ctx, ctx.message.content)
        player = self.bot.music.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Ничего не играет и да... :mute:')

        await ctx.send('⏭ | Пропущена.')
        await player.skip()

    @commands.command(name='repeat', aliases=["stop repeat"])
    async def repeat(self, ctx):
        await ctx.message.delete()
        await command_user(ctx, ctx.message.content)
        player = self.bot.music.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Ничего не играет :mute:')

        # меняем флаг повтора
        player.repeat = not player.repeat

        await ctx.send('🔁 |  Песни крутятся' + ('enabled' if player.repeat else 'disabled'))

    @commands.command(name='pause', aliases=['resume'], help='get song paused')
    async def pause(self, ctx):
        await ctx.message.delete()
        await command_user(ctx, ctx.message.content)
        player = self.bot.music.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Ничего не играет :mute:')

        if player.paused:
            await player.set_pause(False)
            await ctx.send('▶ | Песня возобновлена')
        else:
            await player.set_pause(True)
            await ctx.send('⏸ | Песня приостановлена')

    @commands.command(name='text', help='lyric')
    async def text(self, ctx):
        await ctx.message.delete()
        await command_user(ctx, ctx.message.content)
        player = self.bot.music.player_manager.get(ctx.guild.id)
        for msg in await get_lyric(player.current.title):
            await ctx.send(msg)

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
        else:
            await ctx.send("Зайди в голосовой канал")

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            await self.connect_to(guild_id, None)
        if isinstance(event, lavalink.events.TrackStartEvent):
            print("TrackStartEvent")
            await self.now(self.ctx)

    async def connect_to(self, guild_id: int, channel_id: str):
        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)

    @commands.command(name="help", aliases=['h'])
    async def help(self, ctx):
        em = discord.Embed(colour=discord.Colour(0xFF69B4))
        em.set_author(name="**Список команд**")


def setup(bot):
    bot.add_cog(Music(bot))
