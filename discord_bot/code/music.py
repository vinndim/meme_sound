import math
import os
import discord
from discord_components import DiscordComponents, SelectOption, Select, ButtonStyle, Button
from discord.ext import commands
import lavalink
from discord import utils
import aiosqlite
from text_song import get_lyric, get_normal_title


async def command_user(ctx, msg):
    em = discord.Embed(colour=ctx.message.author.color, title=f"Command by "
                                                              f"{ctx.message.author.display_name}  |  "
                                                              f"<{msg}>")
    await ctx.send(embed=em)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.music = lavalink.Client(self.bot.user.id)
        self.bot.music.add_node('localhost', 7000, 'testing', 'in', 'music-node')
        self.bot.add_listener(self.bot.music.voice_update_handler, 'on_socket_response')
        self.bot.music.add_event_hook(self.track_hook)
        self.db_path = os.path.abspath('../..') + "/web_site/db/users.db"
        self.ctx = None
        self.msg_now = None

    @commands.command(name="menu")
    async def menu(self, ctx, again=False, pause=False):
        pause_flag = pause
        if not again:
            await ctx.message.delete()
            await command_user(ctx, ctx.message.content)
        if not pause:
            pause_str = "Остановить"
            pause_emoji = "⏸"
        else:
            pause_str = "Продолжить"
            pause_emoji = "▶"
        btns = await ctx.send(components=[Button(label="Повторить", emoji="🔄"),
                                          Button(label="Следующий", emoji="⏭"),
                                          Button(label=pause_str, emoji=pause_emoji),
                                          ])
        responce = await self.bot.wait_for("button_click")
        if responce.channel == ctx.channel:
            if responce.component.label == "Повторить":
                await self.repeat(ctx, True)
            if responce.component.label == "Следующий":
                await self.skip(ctx, True)
            if responce.component.label == "Остановить":
                await self.pause(ctx, True)
                pause_flag = True
            if responce.component.label == "Продолжить":
                await self.pause(ctx, True)
                pause_flag = False
            await btns.delete()
            await self.menu(ctx, True, pause_flag)

    @commands.command(name="pl")
    async def user_playlist(self, ctx, *, playlist_name):
        user_id = ctx.message.author.id
        db = await aiosqlite.connect(self.db_path)
        cursor = await db.execute('''SELECT name FROM songs 
        WHERE playlist_id = (SELECT id FROM playlist WHERE (name=? AND 
        user_id=(SELECT id FROM users WHERE user_id = ?)))''', [playlist_name, user_id])
        tracks = await cursor.fetchall()
        await cursor.close()
        await db.close()
        if tracks:
            for query in tracks:
                await self.add_song_to_player(query[0], ctx)
        else:
            await ctx.send("Плейлист не найден :cry:")

    async def add_song_to_player(self, query, ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        results = await player.node.get_tracks(query)
        if not results or not results['tracks']:
            return await ctx.send('Song not found :x: Please try again :mag_right:')
        em = discord.Embed(colour=discord.Colour(0xFF69B4))
        if results['loadType'] == 'PLAYLIST_LOADED':
            tracks = results['tracks']
            for track in tracks:
                player.add(requester=ctx.author.id, track=track)
            em.title = 'Playlist Enqueued!'
            em.description = f'{results["playlistInfo"]["name"]} - {len(tracks)} tracks'
        else:
            track = results['tracks'][0]
            em.title = 'Track Enqueued'
            em.description = f'{track["info"]["title"]}'
            em.set_thumbnail(url=f"http://i.ytimg.com/vi/{track['info']['identifier']}/hqdefault.jpg")
            em.add_field(name='Channel', value=track['info']['author'])
            if track['info']['isStream']:
                duration = 'Live'
            else:
                duration = lavalink.format_time(track['info']['length']).lstrip('00:')
            em.add_field(name='Duration', value=duration)
            track = lavalink.models.AudioTrack(track, ctx.author.id, recommended=True)
            player.add(requester=ctx.author.id, track=track)
            self.ctx = ctx
        if not player.is_playing:
            await player.play()
        else:
            msg = await ctx.send(embed=em)
            await msg.delete(delay=5)

    @commands.command(name='play', aliases=['p', 'sing', '100-7'])
    async def play(self, ctx, *, query):
        query = query.strip('<>')
        if not query.startswith('http'):
            await ctx.message.delete()
            await command_user(ctx, ctx.message.content)
            query = f'ytsearch:{query}'
        await self.add_song_to_player(query, ctx)

    @commands.command(name='queue', aliases=['q', 'playlist'])
    async def queue(self, ctx, page: int = 1):
        await ctx.message.delete()
        await command_user(ctx, ctx.message.content)
        player = self.bot.music.player_manager.get(ctx.guild.id)
        if not player.queue:
            return await ctx.send('Ничего не добавлено :cd:')
        items_per_page = 10
        pages = math.ceil(len(player.queue) / items_per_page)
        start = (page - 1) * items_per_page
        end = start + items_per_page
        queue_list = ''
        for i, track in enumerate(player.queue[start:end], start=start):
            queue_list += f'`{i + 1}.` **{track.title}**\n'
        embed = discord.Embed(colour=discord.Colour(0xFF69B4),
                              description=f'**{len(player.queue)} tracks**\n\n{queue_list}')
        embed.set_footer(text=f'{page}/{pages}')
        await ctx.send(embed=embed)

    @commands.command(name='now', aliases=['np'])
    async def now(self, ctx, user=True):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        if user:
            await ctx.message.delete()
            await command_user(ctx, ctx.message.content)
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
            song = f'{await get_normal_title(player.current.title)}\n`{pos} {bar} {dur}`'
            em = discord.Embed(colour=discord.Colour(0xFF69B4), description=song)
            em.set_author(name="Сейчас играет",
                          icon_url="https://media.giphy.com/media/LIQKmZU1Jm1twCRYaQ/giphy.gif")
            em.set_thumbnail(url=f"http://i.ytimg.com/vi/{player.current.identifier}/hqdefault.jpg")
            self.msg_now = await ctx.send(embed=em, delete_after=10)
            await self.bot.change_presence(
                activity=discord.Activity(type=discord.ActivityType.listening,
                                          name=await get_normal_title(player.current.title)))
        else:
            member = utils.find(lambda m: m.id == ctx.author.id, ctx.guild.members)
            if member is not None and member.voice is not None:
                await ctx.send('Ничего не играет :mute:')

    @commands.command(name='skip', aliases=['forceskip', 'fs', 'next'])
    async def skip(self, ctx, menu=False):
        if not menu:
            await ctx.message.delete()
            await command_user(ctx, ctx.message.content)
        player = self.bot.music.player_manager.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send('Ничего не играет и да... :mute:')
        await ctx.send('⏭ | Пропущена.')
        await player.skip()

    @commands.command(name='repeat', aliases=["stop repeat"])
    async def repeat(self, ctx, menu=False):
        if not menu:
            await ctx.message.delete()
            await command_user(ctx, ctx.message.content)
        player = self.bot.music.player_manager.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send('Ничего не играет :mute:')
        # меняем флаг повтора
        player.repeat = not player.repeat
        await ctx.send('🔁 | ' + ('Песни крутятся' if player.repeat else 'Песни не крутятся'))

    @commands.command(name='pause', aliases=['resume'], help='get song paused')
    async def pause(self, ctx, menu):
        if not menu:
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

    @commands.command(name='remove', aliases=['pop'])
    async def remove(self, ctx, index: int):
        await ctx.message.delete()
        await command_user(ctx, ctx.message.content)
        player = self.bot.music.player_manager.get(ctx.guild.id)
        if not player.queue:
            return await ctx.send('Nothing queued :cd:')
        if index > len(player.queue) or index < 1:
            return await ctx.send('Index has to be >=1 and <=queue size')
        index = index - 1
        removed = player.queue.pop(index)
        await ctx.send('Removed ' + removed.title + ' from the queue.')

    @commands.command(name='text', help='lyric')
    async def text(self, ctx):
        await ctx.message.delete()
        await command_user(ctx, ctx.message.content)
        player = self.bot.music.player_manager.get(ctx.guild.id)
        for msg in await get_lyric(player.current.title):
            await ctx.send(msg)

    async def cog_before_invoke(self, ctx):
        """ Command before-invoke handler. """
        guild_check = ctx.guild is not None

        if guild_check:
            await self.ensure_voice(ctx)
            #  Ensure that the bot and command author share a mutual voicechannel.

        return guild_check

    async def ensure_voice(self, ctx):
        """ This check ensures that the bot and command author are in the same voicechannel. """
        player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        should_connect = ctx.command.name in ('play',)

        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandInvokeError('Join a voice channel first :loud_sound:')

        if not player.is_connected:
            if not should_connect:
                raise commands.CommandInvokeError('Not connected :mute:')

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:  # Check user limit too?
                raise commands.CommandInvokeError(
                    'I need the `CONNECT` and `SPEAK` permissions. :disappointed_relieved:')

            player.store('channel', ctx.channel.id)
            player.clear()
            await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                raise commands.CommandInvokeError('You need to be in my voice channel :loud_sound:')

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            await self.connect_to(guild_id, None)
        if isinstance(event, lavalink.events.TrackStartEvent):
            print("TrackStartEvent")
            ctx = event.player.fetch('channel')
            if ctx:
                ctx = self.bot.get_channel(ctx)
                if ctx:
                    em = discord.Embed(colour=discord.Colour(0xFF69B4),
                                       description=await get_normal_title(event.player.current.title))
                    em.set_author(name="Сейчас играет",
                                  icon_url="https://media.giphy.com/media/LIQKmZU1Jm1twCRYaQ/giphy.gif")
                    await self.bot.change_presence(
                        activity=discord.Activity(type=discord.ActivityType.listening,
                                                  name=await get_normal_title(event.player.current.title)))
                    await ctx.send(embed=em, delete_after=5)

    async def connect_to(self, guild_id: int, channel_id: str):
        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)

    def cog_unload(self):
        """ Cog unload handler. This removes any event hooks that were registered. """
        self.bot.music._event_hooks.clear()


def setup(bot):
    bot.add_cog(Music(bot))
