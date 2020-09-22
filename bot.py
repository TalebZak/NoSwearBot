import os

import discord
from dotenv import load_dotenv
from utils import is_substring
from discord.ext import commands
import sqlite3

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='!', case_insensitive=True)


@bot.command(description='blacklists a word if it was not blacklisted already', brief='blacklists a word')
async def add(ctx, word):
    if not word:
        await ctx.send('you are not adding anything')
        return
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    guild_id = ctx.guild.id
    query = '''SELECT word FROM badwords WHERE guild_id=? AND word=?'''
    cursor.execute(query, (guild_id, word))
    word_result = cursor.fetchone()
    if word_result:
        await ctx.send('this word already exists')
    else:
        query = '''INSERT INTO badwords(guild_id, word)
                          VALUES (?,?)'''
        cursor.execute(query, (guild_id, word))
        db.commit()
        await ctx.send(f'{word} was added to the blacklist')


@bot.command(description='lists all the words that were blacklisted in the server', brief='lists all blacklisted words')
async def listwords(ctx):
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    guild_id = ctx.guild.id
    cursor.execute(f'SELECT word FROM badwords WHERE guild_id={guild_id}')
    words = [swear[0] for swear in cursor.fetchall()]
    if not words:
        await ctx.send('There are no blacklisted words')
        return
    wordlist = ''.join([f'-{word}\n' for word in words])
    await ctx.send(f'the swearwords in this server are:\n{wordlist}')


@bot.command(description='allows the creator of the server to remove a word from the blacklist', brief='removes a blacklisted word')
async def delete(ctx, word=None):
    if ctx.author != ctx.guild.owner:
        await ctx.send("Only the server owners are allowed to change the blacklist")
        return
    if not word:
        await ctx.send("Your command doesn't contain a word to delete")
        return
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    guild_id = ctx.guild.id
    query = '''SELECT word FROM badwords WHERE guild_id=? AND word=?'''
    cursor.execute(query, (guild_id, word))

    word_result = cursor.fetchone()
    if not word_result:
        await ctx.send(f'{word} is not blacklisted')
    else:
        query = '''DELETE FROM badwords WHERE word=? AND guild_id=?'''
        cursor.execute(query, (word, guild_id))
        db.commit()
        await ctx.send(f'{word} was successfully deleted')


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!\n')


@bot.listen('on_message')
async def delete_on_swear(message):
    if not message:
        return
    if message.content.lower().startswith(('!add', '!delete')):
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
    if bot.user == message.author:
        return
    for swearword in swears:
        if not message.channel.is_nsfw() and is_substring(message.content.lower(), swearword):
            await message.delete()
            await message.author.create_dm()
            await message.author.dm_channel.send(
                f'Hi {message.author}, you sent a message containing the following word: {swearword}'
            )
            return


bot.run(TOKEN)
