import math
import os
from pprint import pprint

import discord
from discord_components import Button
from discord.ext import commands
import lavalink
from discord import utils, Embed
import aiosqlite
from text_song import get_lyric, get_normal_title, get_album, parser_lyric
from sql_query import PLAYLIST_QUERY
from help import command_user, get_list_commands


async def stop(ctx, ch):
    print("need leave")


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.music = lavalink.Client(self.bot.user.id)
        self.bot.music.add_node('localhost', 7000, 'testing', 'in', 'music-node')
        self.bot.add_listener(self.bot.music.voice_update_handler, 'on_socket_response')
        self.bot.music.add_event_hook(self.track_hook)
        self.db_path = os.path.abspath('../..') + "/web_site/db/users.db"

    @commands.command(name="menu")
    async def menu(self, ctx, again=False, pause=False, repeat=False):
        pause_flag = pause
        repeat_flag = repeat
        if not again:
            await ctx.message.delete()
            await command_user(ctx, ctx.message.content)
        if not pause_flag:
            pause_str = "Остановить"
            pause_emoji = "⏸"
        else:
            pause_str = "Продолжить"
            pause_emoji = "▶"
        if not repeat_flag:
            repeat_str = "Повторить"
        else:
            repeat_str = "Остановить повторение"
        btns = await ctx.send(components=[Button(label=repeat_str, emoji="🔄"),
                                          Button(label="Следующий", emoji="⏭"),
                                          Button(label=pause_str, emoji=pause_emoji),
                                          Button(label="Текст песни", emoji="📖")])
        responce = await self.bot.wait_for("button_click")
        await btns.delete()
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
            if responce.component.label == "Текст песни":
                await self.text(ctx, True)
            await self.menu(ctx, True, pause_flag)

    @commands.command(name="pl")
    async def user_playlist(self, ctx, *, playlist_name):
        user_id = ctx.message.author.id
        db = await aiosqlite.connect(self.db_path)
        cursor = await db.execute(PLAYLIST_QUERY, [playlist_name, user_id])
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

    @commands.command(name='disconnect', aliases=['dis', 'stop', 'leave'])
    async def disconnect(self, ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)

        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            return await ctx.send('You\'re not in my voice channel :loud_sound:')

        if not player.is_connected:
            return await ctx.send('Not connected :mute:')

        player.queue.clear()
        # Stop the current track so Lavalink consumes less resources.
        await player.stop()
        # Disconnect from the voice channel.
        await self.connect_to(ctx.guild.id, None)
        await ctx.send('Disconnected :mute:')
        await self.bot.change_presence(status=discord.Status.idle, activity=discord.Game(name="Nothing"))

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
            await ctx.send(embed=em, delete_after=10)
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
        await ctx.send('⏭ | Пропущена.', delete_after=5)
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
        await ctx.send('🔁 | ' + ('Песни крутятся' if player.repeat else 'Песни не крутятся'), delete_after=5)

    @commands.command(name='pause', aliases=['resume'])
    async def pause(self, ctx, menu):
        if not menu:
            await ctx.message.delete()
            await command_user(ctx, ctx.message.content)
        player = self.bot.music.player_manager.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send('Ничего не играет :mute:')
        if player.paused:
            await player.set_pause(False)
            await ctx.send('▶ | Песня возобновлена', delete_after=5)
        else:
            await player.set_pause(True)
            await ctx.send('⏸ | Песня приостановлена', delete_after=5)

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
        await ctx.send('Removed ' + removed.title + ' from the queue.', delete_after=5)

    @commands.command(name='text', help='lyric')
    async def text(self, ctx, menu=False):
        if not menu:
            await ctx.message.delete()
            await command_user(ctx, ctx.message.content)
        player = self.bot.music.player_manager.get(ctx.guild.id)
        album_flag = False
        album_link = ""
        query_result = ""

        def check(m):
            return m.author.id == ctx.author.id

        for msg in await get_lyric(player.current.title):
            if msg.startswith("https"):
                album_flag = True
                album_link = msg
            else:
                await ctx.send(msg)
        if album_flag:
            links, titles = await get_album(album_link)
            # pprint(await get_album(album_link))
            for n in range(len(titles)):
                query_result = query_result + f'{n + 1} {titles[n]}\n'
            embed = Embed(colour=discord.Colour(0xFF69B4), title="Выберите песню")
            embed.description = query_result
            await ctx.send(embed=embed)
            response = await self.bot.wait_for('message', check=check)
            for new_msg in await parser_lyric(links[int(response.content) - 1]):
                await ctx.send(new_msg)

    @commands.command(name='help')
    async def help(self, ctx):
        await ctx.message.delete()
        await command_user(ctx, ctx.message.content)
        await ctx.send(embed=await get_list_commands())

    @play.before_invoke
    async def ensure_voice(self, ctx):
        """ This check ensures that the bot and command author are in the same voicechannel. """
        player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        should_connect = ctx.command.name in ('play', 'pl')
        try:
            if not ctx.author.voice or not ctx.author.voice.channel:
                await ctx.send("Нужно зайти в голосовой чат :loud_sound:")
                pprint(commands.CommandInvokeError('Join a voice channel first :loud_sound:'))

            if not player.is_connected:
                if not should_connect:
                    await ctx.send("Не подключен :mute:")
                    print(commands.CommandInvokeError)

                permissions = ctx.author.voice.channel.permissions_for(ctx.me)

                if not permissions.connect or not permissions.speak:  # Check user limit too?
                    await ctx.send("Дайте мне права, пожалуйста:disappointed_relieved:")
                    pprint(commands.CommandInvokeError)

                player.store('channel', ctx.channel.id)
                await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
            else:
                if int(player.channel_id) != ctx.author.voice.channel.id:
                    await ctx.send("Нужно зайти в голосовой чат :disappointed_relieved:")
                    pprint(commands.CommandInvokeError)
        except Exception as e:
            print(e)

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            await self.connect_to(guild_id, None)
        if isinstance(event, lavalink.events.TrackStartEvent):
            print("TrackStartEvent")
            channel_id = event.player.fetch('channel')
            print(event.player)
            if channel_id:
                ctx = self.bot.get_channel(channel_id)
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
