import os

import discord
from dotenv import load_dotenv
from utils import is_substring

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD_TOKEN')
client = discord.Client()


@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break
    print(f'{client.user} has connected to Discord!\n'
          f'Discord ID:{guild.id}')
    members = [member.name for member in guild.members]
    print(f'\n{members}')


@client.event
async def on_message(message):
    swears = ['zbi', 'idk fih', 'fuck', 'shit']
    if client.user == message.author:
        return
    for swearword in swears:
        if is_substring(message.content.lower(), swearword):
            await message.delete()
            await message.author.create_dm()
            await message.author.dm_channel.send(
                f'Hi {message.author}, you sent a message containing the following word: {swearword}'
            )


client.run(TOKEN)
