import discord
from discord.ext import commands

from discord_bot.support_code.user_info import get_info
from discord_bot.support_code.work_with_commands import command_user, get_list_commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help')
    async def help(self, ctx):
        await ctx.message.delete()
        await command_user(ctx, ctx.message.content)
        await ctx.send(embed=await get_list_commands())

    @commands.command(name="info")
    async def info_user(self, ctx, member=None):
        await ctx.message.delete()
        await command_user(ctx, ctx.message.content)
        em = await get_info(ctx, member)
        await ctx.send(embed=em)

    @commands.command(name='site')
    async def get_web_site(self, ctx):
        await ctx.message.delete()
        await command_user(ctx, ctx.message.content)
        em = discord.Embed(colour=discord.Colour(0xFF69B4), title='Наш сайт',
                           description="http://memesoundwebsitenew.herokuapp.com")
        await ctx.send(embed=em)

    def cog_unload(self):
        """ Cog unload handler. This removes any event hooks that were registered. """
        self.bot.music._event_hooks.clear()


def setup(bot):
    bot.add_cog(Help(bot))
