vc.play(discord.FFmpegPCMAudio(song := await YTDLSource.from_url(url,
                                                                             loop=self.bot.loop, stream=True),
                                           **FFMPEG_OPTIONS))