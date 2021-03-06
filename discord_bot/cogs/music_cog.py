import math
from random import randint

import discord
import requests
from discord_components import Button
from discord.ext import commands
import lavalink
from discord import utils, Embed

from discord_bot.support_code.lyric_parser import get_lyric, get_normal_title, get_album, parser_lyric
from discord_bot.support_code.yandex_response import get_album_yandex


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.music = lavalink.Client(self.bot.user.id)
        self.bot.music.add_node('localhost', 7000, 'testing', 'in', 'music-node')
        self.bot.add_listener(self.bot.music.voice_update_handler, 'on_socket_response')
        self.bot.music.add_event_hook(self.track_hook)
        self.menu_channel_btns = {}
        self.now_playing_msg = {}
        self.last_ctx = {}

    @commands.command(name="menu")
    async def menu(self, ctx,
                   add_song=False, again=False,
                   pause=False, repeat=False):
        if ctx.guild.id in self.menu_channel_btns.keys():
            if not again and not add_song:
                await self.menu_channel_btns[ctx.guild.id].delete()
                player = self.bot.music.player_manager.get(ctx.guild.id)
                pause = player.paused
                repeat = player.repeat
            if add_song:
                await self.menu_channel_btns[ctx.guild.id].delete()

        pause_flag = pause
        repeat_flag = repeat
        if not pause_flag:
            pause_str = "Остановить"
            pause_emoji = "⏸"
        else:
            pause_str = "Продолжить"
            pause_emoji = "▶"
        if not repeat_flag:
            repeat_str = "Повторить"
        else:
            repeat_str = "Не повторять"
        btns = await ctx.send(components=[Button(label=repeat_str, emoji="🔄"),
                                          Button(label="Следующий", emoji="⏭"),
                                          Button(label=pause_str, emoji=pause_emoji),
                                          Button(label="Текст песни", emoji="📖")])
        self.menu_channel_btns[ctx.guild.id] = btns
        responce = await self.bot.wait_for("button_click")
        await btns.delete()
        if responce.channel == ctx.channel:
            if responce.component.label == "Повторить":
                await self.repeat(ctx)
                repeat_flag = True
            if responce.component.label == "Не повторять":
                await self.repeat(ctx)
                repeat_flag = False
            if responce.component.label == "Следующий":
                pause_flag = False
                await self.skip(ctx)
            if responce.component.label == "Остановить":
                await self.pause(ctx)
                pause_flag = True
            if responce.component.label == "Продолжить":
                await self.pause(ctx)
                pause_flag = False
            if responce.component.label == "Текст песни":
                await self.text(ctx)
            await self.menu(ctx, again=True, pause=pause_flag, repeat=repeat_flag)

    @commands.command(name="pl")
    async def user_playlist(self, ctx, *, user_playlist=None):
        user_id = ctx.message.author.id
        responce = requests.get(f"https://memesoundwebsite.herokuapp.com/api/{user_id}")
        r_json = responce.json()
        playlists = r_json["playlists"]
        if user_playlist:
            if user_playlist.isdigit():
                playlist_name = playlists[int(user_playlist) - 1]  # воспризведение плейлиста по номеру в списке
            else:
                playlist_name = user_playlist
            msg = await ctx.send("Альбом добавляется...")
            for s in range(len(playlist := r_json[f'songs {playlist_name}'])):
                if playlist[s].startswith("http"):
                    query_search = playlist[s]
                else:
                    query_search = f"ytsearch:{playlist[s]}"
                if s + 1 == len(playlist):
                    em = discord.Embed(colour=discord.Colour(0xFF69B4), title=playlist_name,
                                       description=f"Добавлено {len(playlist)} треков")
                    em.set_thumbnail(url=r_json[f'image {playlist_name}'])
                    em.add_field(name="Длительность", value=r_json[f'length {playlist_name}'])
                    em.set_footer(text=ctx.message.author)
                    await msg.delete()
                    await ctx.send(embed=em)
                await self.add_song_to_player(query_search, ctx, playlist_flag=True, play=s + 1 == len(playlist))
        else:
            em = discord.Embed(colour=discord.Colour(0xFF69B4), title="Ваши Альбомы")
            for n, pl in enumerate(r_json["playlists"]):
                em.add_field(name=f"{n + 1}) {pl}",
                             value=f"Количество треков: {len(r_json[f'songs {pl}'])}", inline=False)
                em.add_field(name="Длительность", value=r_json[f'length {pl}'])
                em.set_footer(text=ctx.message.author)
            await ctx.send(embed=em)

    async def add_song_to_player(self, query, ctx, playlist_flag=False, play=True, random_track=False):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        em = discord.Embed(colour=discord.Colour(0xFF69B4))
        results = await player.node.get_tracks(song := get_normal_title(query))
        if not results or not results['tracks']:
            return await ctx.send(f'Песня {song.replace("ytsearch:", "")} не найдена :x:')
        if results['loadType'] == 'PLAYLIST_LOADED' and not random_track:
            tracks = results['tracks']
            for track in tracks:
                player.add(requester=ctx.author.id, track=track)
            em.title = 'Плейлист добавлен!'
            em.description = f'{results["playlistInfo"]["name"]} - {len(tracks)} треков'
        else:
            if random_track:
                random_number = randint(0, len(results['tracks']) - 1)
                track = results['tracks'][random_number]
            else:
                track = results['tracks'][0]
            em.title = 'Трек добавлен'
            em.description = f'{track["info"]["title"]}'
            em.set_thumbnail(url=f"http://i.ytimg.com/vi/{track['info']['identifier']}/hqdefault.jpg")
            em.add_field(name='Канал', value=track['info']['author'])
            if track['info']['isStream']:
                duration = 'Live'
            else:
                duration = lavalink.format_time(track['info']['length']).lstrip('00:')
            em.add_field(name='Длительность', value=duration)
            track = lavalink.models.AudioTrack(track, ctx.author.id)
            player.add(requester=ctx.author.id, track=track)
        if not player.is_playing and play is True:
            await player.play()
            await self.menu(ctx, add_song=True, pause=player.paused, repeat=player.repeat)
        else:
            if not playlist_flag:
                await ctx.send(embed=em)
                # await self.menu(ctx, add_song=True, pause=player.paused, repeat=player.repeat)

    @commands.command(name='play', aliases=['p', 'sing', '100-7'])
    async def play(self, ctx, *, query):
        query = query.strip('<>')
        if not query.startswith('http'):
            query = f'ytsearch:{query}'
        await self.add_song_to_player(query, ctx)

    @commands.command(name='yandex', aliases=['y'])
    async def yandex_music_play(self, ctx, *, query):
        response = await get_album_yandex(query)
        player = self.bot.music.player_manager.get(ctx.guild.id)
        msg = await ctx.send("Альбом загружается...")
        if response["lst_executors_tr"] is None:
            playlist = response['lst_songs_titles']
        else:
            playlist = response["lst_executors_tr"]
        for song_number in range(len(playlist)):
            if response["lst_excutor_album"] is not None:
                query_search = f'ytsearch:{playlist[song_number]} ' \
                               f'{" ".join(response["lst_excutor_album"])}'
            else:
                query_search = f'ytsearch:{playlist[song_number]} ' \
                               f'{response["lst_executors_tr"][song_number]}'
            if song_number + 1 == len(playlist):
                em = discord.Embed(colour=discord.Colour(0xFF69B4),
                                   description=" ".join(response["lst_excutor_album"])
                                   if response["lst_excutor_album"] is not None
                                   else f'Количество треков: {len(playlist)}')
                em.set_author(name=response["album_title"])
                em.set_thumbnail(url=response["im_album"])
                em.set_footer(text="YandexMusic",
                              icon_url="https://yastatic.net/s3/doc-binary/freeze/ru/music"
                                       "/eb46606ef5c2f78e06c7289d712e9d7e7a3712a1.png")
                await msg.delete()
                await ctx.send(embed=em)
            await self.add_song_to_player(query_search, ctx, playlist_flag=True,
                                          play=song_number + 1 == len(playlist))
        await self.menu(ctx, add_song=True, pause=player.paused, repeat=player.repeat)

    @commands.command(name='queue', aliases=['q', 'playlist'])
    async def queue(self, ctx, page: int = 1):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        if not player.queue:
            return await ctx.send('Ничего не добавлено :cd:', delete_after=5)
        items_per_page = 10
        pages = math.ceil(len(player.queue) / items_per_page)
        start = (page - 1) * items_per_page
        end = start + items_per_page
        queue_list = ''
        for i, track in enumerate(player.queue[start:end], start=start):
            queue_list += f'`{i + 1}.` **{get_normal_title(track.title)}**\n'
        embed = discord.Embed(colour=discord.Colour(0xFF69B4),
                              description=f'**{len(player.queue)} tracks**\n\n{queue_list}')
        embed.set_footer(text=f'{page}/{pages}')
        await ctx.send(embed=embed)

    @commands.command(name='disconnect', aliases=['dis', 'stop', 'leave'])
    async def disconnect(self, ctx, leave_users=False):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        if not leave_users:
            if not player.is_connected:
                return await ctx.send('Не подключён :mute:', delete_after=5)
            if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
                return await ctx.send('Вы не в моём голосовом чате  :loud_sound:', delete_after=5)
            await self.connect_to(ctx.guild.id, None)
            await ctx.send('Отключен :mute:', delete_after=5)

        player.queue.clear()
        # Stop the current track so Lavalink consumes less resources.
        await player.stop()
        # Disconnect from the voice channel.
        if ctx.guild.id in self.menu_channel_btns.keys():
            await self.menu_channel_btns[ctx.guild.id].delete()
            self.menu_channel_btns.pop(ctx.guild.id)
        await self.bot.change_presence(status=discord.Status.idle, activity=discord.Game(name="Nothing"))

    @commands.command(name='now', aliases=['np'])
    async def now(self, ctx, seek=None):
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
            song = f'{get_normal_title(player.current.title)}\n`{pos} {bar} {dur}`'
            em = discord.Embed(colour=discord.Colour(0xFF69B4), description=song)
            em.set_author(name="Сейчас играет" if seek is None else seek,
                          icon_url="https://media.giphy.com/media/LIQKmZU1Jm1twCRYaQ/giphy.gif" if seek is None else '')
            em.set_thumbnail(url=f"http://i.ytimg.com/vi/{player.current.identifier}/hqdefault.jpg")
            await ctx.send(embed=em, delete_after=10)
            await self.bot.change_presence(
                activity=discord.Activity(type=discord.ActivityType.listening,
                                          name=get_normal_title(player.current.title)))
        else:
            member = utils.find(lambda m: m.id == ctx.author.id, ctx.guild.members)
            if member is not None and member.voice is not None:
                await ctx.send('Ничего не играет :mute:', delete_after=5)

    @commands.command(name='skip', aliases=['forceskip', 'fs', 'next'])
    async def skip(self, ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send('Ничего не играет и да... :mute:')
        await ctx.send('⏭ | Пропущена.', delete_after=5)
        await player.skip()

    @commands.command(name='repeat', aliases=["stop repeat"])
    async def repeat(self, ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send('Ничего не играет :mute:', delete_after=5)
        # меняем флаг повтора
        player.repeat = not player.repeat
        await ctx.send('🔁 | ' + ('Песни крутятся' if player.repeat else 'Песни не крутятся'), delete_after=5)

    @commands.command(name='pause', aliases=['resume'])
    async def pause(self, ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send('Ничего не играет :mute:')
        if player.paused:
            await player.set_pause(False)
            await ctx.send('▶ | Песня возобновлена', delete_after=5)
        else:
            await player.set_pause(True)
            await ctx.send('⏸ | Песня приостановлена', delete_after=5)

    @commands.command(name='volume', aliases=['vol'])
    async def volume(self, ctx, volume: int = None):
        player = self.bot.music.player_manager.get(ctx.guild.id)

        if not volume:
            return await ctx.send(f'🔈 | {player.volume}%')

        await player.set_volume(volume)
        await ctx.send(f'🔈 | Звук на {player.volume}%')

    @commands.command(name='remove', aliases=['pop'])
    async def remove(self, ctx, index: int):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        if not player.queue:
            return await ctx.send('Нечего удалять :cd:')
        if index > len(player.queue) or index < 1:
            return await ctx.send('Такой песни в списке нет')
        index = index - 1
        removed = player.queue.pop(index)
        await ctx.send('Удалён ' + removed.title + ' из очереди.', delete_after=5)

    @commands.command(name='text', help='lyric')
    async def text(self, ctx, *, query=None):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        album_flag = False
        album_link = ""
        query_result = ""

        def check(m):
            return m.author.id == ctx.author.id

        async with ctx.typing():
            for msg in get_lyric(query if query is not None else player.current.title):
                if msg.startswith("https"):
                    album_flag = True
                    album_link = msg
                else:
                    await ctx.send(msg)
        if album_flag:
            links, titles = get_album(album_link)
            # pprint(await get_album(album_link))
            for n in range(len(titles)):
                query_result = query_result + f'{n + 1} {titles[n]}\n'
            embed = Embed(colour=discord.Colour(0xFF69B4), title="Выберите песню")
            embed.description = query_result
            await ctx.send(embed=embed)
            response = await self.bot.wait_for('message', check=check)
            async with ctx.typing():
                for new_msg in parser_lyric(links[int(response.content) - 1]):
                    await ctx.send(new_msg)

    @commands.command(name='seek')
    async def seek(self, ctx, seconds=None):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send('Ничего не играет :mute:')

        if not seconds:
            return await ctx.send('Укажите на сколько нужно перемотать :fast_forward:')
        try:
            track_time = player.position + int(seconds) * 1000
            await player.seek(track_time)
        except ValueError:
            return await ctx.send('Неправильный формат :clock3:')
        await self.now(ctx, seek='⏩Трек перемотан⏩')

    @commands.command(name='shuffle')
    async def shuffle(self, ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Ничего не играет :mute:')

        player.shuffle = not player.shuffle

        await ctx.send('🔀 | Перемешивание ' + ('включено' if player.shuffle else 'отклчено'))

    async def ensure_voice(self, ctx):
        """ This check ensures that the bot and command author are in the same voicechannel. """
        player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        should_connect = ctx.command.name in ('play', 'yandex', "pl", 'mp', 'gachi', 'ph', "dota")

        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("Нужно зайти в голосовой чат :loud_sound:", delete_after=5)
            raise commands.CommandInvokeError("Нужно зайти в голосовой чат")

        if not player.is_connected:
            if not should_connect:
                await ctx.send("Не подключен :mute:")
                raise commands.CommandInvokeError("Не подключен")
            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:  # Check user limit too?
                await ctx.send("Дайте мне права, пожалуйста:disappointed_relieved:", delete_after=5)
                raise commands.CommandInvokeError("Нет прав")

            player.store('channel', ctx.channel.id)
            await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                await ctx.send("Нужно зайти в голосовой чат :disappointed_relieved:", delete_after=5)
                raise commands.CommandInvokeError("Нужно зайти в голосовой чат")

    @commands.command(name='mp')
    async def mashup(self, ctx):
        playlists = ('https://youtube.com/playlist?list=PLVuMkE7ik-_OQMhz_dfC1-LHdJqjJhrbv',
                     "https://www.youtube.com/playlist?list=PLmv4zqE8jsbfgx8jElUqkR_xTIbwwlin1",
                     "https://youtube.com/playlist?list=PL38lkblVbb0G6BKn8JFVmKXAG72_FdhI5")
        await self.add_song_to_player(ctx=ctx,
                                      query=playlists[randint(0, 2)],
                                      random_track=True)

    @commands.command(name='gachi')
    async def gachi(self, ctx):
        playlists = ('https://www.youtube.com/watch?v=Szyx0aFQDnA&list=PLSv7Sd0hjtkmfXH-Yp4WHzKUqVRkh78cf',
                     'https://youtube.com/playlist?list=PLA51vWSHb3b4wbRFOafRqDMFzGm1P66zQ')
        await self.add_song_to_player(ctx=ctx,
                                      query=playlists[randint(0, 1)],
                                      random_track=True)

    @commands.command(name='ph')
    async def phonk(self, ctx):
        playlists = ('https://youtube.com/playlist?list=PLVHr-EkQ_tTPef8vm-ZrANoNGbz6ol8yh',
                     'https://youtube.com/playlist?list=PLYoZ5NeRgzjfrhsW3ecpWbp9VLxVLwic3')
        await self.add_song_to_player(ctx=ctx,
                                      query=playlists[randint(0, 1)],
                                      random_track=True)

    @commands.command(name='dota')
    async def dota(self, ctx):
        await self.add_song_to_player(ctx=ctx,
                                      query="https://www.youtube.com/playlist?list=PLY6_YYWHG4w1_CNPsjcuqkYLKnlwIhSwT",
                                      random_track=True)

    async def cog_before_invoke(self, ctx):
        """ Command before-invoke handler. """
        guild_check = ctx.guild is not None

        if guild_check:
            await self.ensure_voice(ctx)
            self.last_ctx[ctx.guild.id] = ctx
            #  Ensure that the bot and command author share a mutual voicechannel.

        return guild_check

    async def get_ctx(self, event):
        channel_id = event.player.fetch('channel')
        if channel_id:
            ctx = self.bot.get_channel(channel_id)
            return ctx
        return

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        print(member, before.channel, after.channel)
        if before.channel is not None and after.channel is None:
            print(f'before:{len(before.channel.members)}')
            # Бот выходит, если остаётся один в голосовом чате
            if len(before.channel.members) == 1 and before.channel.members[0].id == self.bot.user.id:
                guild_id = before.channel.members[0].guild.id
                if self.last_ctx.keys():
                    ctx = self.last_ctx[guild_id]
                    player = self.bot.music.player_manager.get(guild_id)
                    await player.set_pause(True)
                    await self.menu_channel_btns[ctx.guild.id].delete()
                    self.menu_channel_btns.pop(ctx.guild.id)
                    await ctx.send('Все вышли из голосового канала. Воспроизведение остановлено | ⏸')

        elif before.channel is None and after.channel is not None:
            print(f'after:{len(after.channel.members)}')
            if len(after.channel.members) > 1 and after.channel.members[0].id == self.bot.user.id:
                if self.last_ctx.keys():
                    guild_id = after.channel.members[0].guild.id
                    ctx = self.last_ctx[guild_id]
                    player = self.bot.music.player_manager.get(guild_id)
                    await self.menu(ctx, add_song=True, pause=player.paused, repeat=player.repeat)

        elif before.channel is not None and after.channel is not None:
            if len(before.channel.members) == 1 and before.channel.members[0].id == self.bot.user.id:
                guild_id = before.channel.members[0].guild.id
                if self.last_ctx.keys():
                    ctx = self.last_ctx[guild_id]
                    player = self.bot.music.player_manager.get(guild_id)
                    await player.set_pause(True)
                    await self.menu_channel_btns[ctx.guild.id].delete()
                    self.menu_channel_btns.pop(ctx.guild.id)
                    await ctx.send('Все перешли в другой канал. Воспроизведение остановлено | ⏸')
            elif len(after.channel.members) > 1 and self.bot.user in after.channel.members:
                if self.last_ctx.keys():
                    guild_id = after.channel.members[0].guild.id
                    ctx = self.last_ctx[guild_id]
                    player = self.bot.music.player_manager.get(guild_id)
                    await self.menu(ctx, add_song=True, pause=player.paused, repeat=player.repeat)
            elif member == self.bot.user and len(after.channel.members) == 1:
                guild_id = after.channel.members[0].guild.id
                ctx = self.last_ctx[guild_id]
                player = self.bot.music.player_manager.get(guild_id)
                await player.set_pause(True)
                await self.menu_channel_btns[ctx.guild.id].delete()
                self.menu_channel_btns.pop(ctx.guild.id)
                await ctx.send('Бота переместили в другой канал. Воспроизведение остановлено | ⏸')
            elif member == self.bot.user and len(after.channel.members) > 1:
                guild_id = after.channel.members[0].guild.id
                ctx = self.last_ctx[guild_id]
                player = self.bot.music.player_manager.get(guild_id)
                await player.set_pause(True)
                await self.menu_channel_btns[ctx.guild.id].delete()
                self.menu_channel_btns.pop(ctx.guild.id)
                # await ctx.send('Бота переместили в другой канал. Воспроизведение остановлено | ⏸')

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            ctx = await self.get_ctx(event)
            if ctx:
                await self.disconnect(ctx, True)
        if isinstance(event, lavalink.events.TrackEndEvent):
            try:
                ctx = await self.get_ctx(event)
                if ctx:
                    if ctx in self.now_playing_msg.keys():
                        await self.now_playing_msg[ctx].delete()
            except Exception as e:
                print(e)

        if isinstance(event, lavalink.events.TrackStartEvent):
            ctx = await self.get_ctx(event)
            if ctx:
                player = self.bot.music.player_manager.get(ctx.guild.id)
                em = discord.Embed(colour=discord.Colour(0xFF69B4),
                                   description=get_normal_title(event.player.current.title))
                em.set_author(name="Сейчас играет 🎵",
                              icon_url="https://media.giphy.com/media/LIQKmZU1Jm1twCRYaQ/giphy.gif")
                em.set_thumbnail(url=f"http://i.ytimg.com/vi/{player.current.identifier}/hqdefault.jpg")
                await self.bot.change_presence(
                    activity=discord.Activity(type=discord.ActivityType.listening,
                                              name=f'{get_normal_title(event.player.current.title)}'))
                msg = await ctx.send(embed=em)
                self.now_playing_msg[ctx] = msg
        if isinstance(event, lavalink.events.TrackExceptionEvent):
            ctx = await self.get_ctx(event)
            if ctx:
                await ctx.send('Ошибка загрузки')
                if ctx in self.now_playing_msg.keys():
                    await self.now_playing_msg[ctx].delete()
                print('Exception')

    async def connect_to(self, guild_id: int, channel_id: str):
        ws = self.bot._connection._get_websocket(guild_id)
        print(f"g_id: {guild_id}")
        await ws.voice_state(str(guild_id), channel_id)

    def cog_unload(self):
        """ Cog unload handler. This removes any event hooks that were registered. """
        self.bot.music._event_hooks.clear()


def setup(bot):
    bot.add_cog(Music(bot))
