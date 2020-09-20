import os

import discord
from dotenv import load_dotenv
from utils import is_substring
from discord.ext import commands
import sqlite3

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD_TOKEN')
client = discord.Client()
bot = commands.Bot(command_prefix='!')


@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)


@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            break
    print(f'{bot.user} has connected to Discord!\n'
          f'Discord ID:{guild.id}')
    members = [member.name for member in guild.members]
    print(f'\n{members}')


@bot.event
async def on_message(message):
    # swears = ['zbi', 'idk fih', 'fuck', 'shit', 'ass']
    if not message:
        return
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    try:
        guild_id = message.guild.id
    except AttributeError:
        return
    cursor.execute(f'SELECT word FROM badwords WHERE guild_id={guild_id}')
    swears = [swear[0] for swear in cursor.fetchall()]
    if not swears:
        return
    if client.user == message.author:
        return
    for swearword in swears:
        if not message.channel.is_nsfw() and is_substring(message.content.lower(), swearword):
            await message.delete()
            await message.author.create_dm()
            await message.author.dm_channel.send(
                f'Hi {message.author}, you sent a message containing the following word: {swearword}'
            )


bot.run(TOKEN)
