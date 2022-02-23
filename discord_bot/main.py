import discord
import os

client = discord.Client()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')


client.run("OTQ1NzE3MTUxODMzMTMzMDc2.YhUNuw.HaAbqz-JU3xditJ2Yja6JAG0yLo")
