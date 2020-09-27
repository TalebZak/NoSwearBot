import os

import discord
from dotenv import load_dotenv
from utils import is_substring
from discord.ext import commands
import sqlite3

load_dotenv()
#Takes the bot's token that I have saved in a .env file and stores in the token variables
TOKEN = os.getenv('DISCORD_TOKEN')
#the commands are called by the command prefix '!', the fact that I made it case insensitive is for Discord mobile users
bot = commands.Bot(command_prefix='!', case_insensitive=True)


@bot.command(description='blacklists a word if it was not blacklisted already', brief='blacklists a word')
async def add(ctx, word=None):
    """This function adds a word to the swears database
        Args:
            ctx: A context variables that refers to the channel, and other details that a command usually requires
            word: The new swear word that the Guild member wants to add to the blacklist(default is None in case a user forgets a word)
        Returns:
            Doesn't have a return value"""
    if not word:
        await ctx.send('you are not adding anything')
        return
    #first connecting to the main database
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    #getting the guild's id from the context to allow mapping
    guild_id = ctx.guild.id
    #searches if the word that a user wants to add to avoid duplicates
    query = '''SELECT word FROM badwords WHERE guild_id=? AND word=?'''
    cursor.execute(query, (guild_id, word))
    word_result = cursor.fetchone()
    if word_result:
        await ctx.send('this word already exists')
    else:
        #if the word doesn't exists it gets inserted into the database
        query = '''INSERT INTO badwords(guild_id, word)
                          VALUES (?,?)'''
        cursor.execute(query, (guild_id, word))
        db.commit()
        await ctx.send(f'{word} was added to the blacklist')


@bot.command(description='lists all the words that were blacklisted in the server', brief='lists all blacklisted words')
async def listwords(ctx):
    """A function that allows a guild member to see all the blacklisted words in the guild
       Args:
            ctx: Context variables required by the command to get details like guild id
       Returns:
            Doesn't have a return value"""
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    guild_id = ctx.guild.id
    cursor.execute(f'SELECT word FROM badwords WHERE guild_id={guild_id}')
    #a list comprehension since the fetchall method returns a tuple in the form of (word,)
    words = [swear[0] for swear in cursor.fetchall()]
    if not words:
        await ctx.send('There are no blacklisted words')
        return
    #basic message formatting for the swearwords
    wordlist = ''.join([f'-{word}\n' for word in words])
    await ctx.send(f'the swearwords in this server are:\n{wordlist}')


@bot.command(description='allows the creator of the server to remove a word from the blacklist', brief='removes a blacklisted word')
async def delete(ctx, word=None):
    """A command that allows the admin to delete swear words and make users able to say it for any reasons. Only the owner has that privilege for one simple
       reason which is avoid any sort of undesired deletion of word that can make others feel uncomfortable
       Args:
           ctx: Context variable for the command to see the guild and author
           word: the word to delete from the blacklist
       Returns:
            Doesn't have a return value"""
    if ctx.author != ctx.guild.owner:
        #in case the author of the command is not the same person as the guild owner
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
        #if the word does not exist already, this message is displayed
        await ctx.send(f'{word} is not blacklisted')
    else:
        query = '''DELETE FROM badwords WHERE word=? AND guild_id=?'''
        cursor.execute(query, (word, guild_id))
        db.commit()
        await ctx.send(f'{word} was successfully deleted')


@bot.event
async def on_ready():
    #used for debugging purposes
    print(f'{bot.user} has connected to Discord!\n')


@bot.listen('on_message')
async def delete_on_swear(message):
    """This function tries to detect whether a message contains a bad word and deletes gthe message, then sends a warning to the message author
        Args:
            message: This is that the author sent and contains details like message's author, channel and other details that would help when working with the bot
        Returns:
            Doesn't have a return type"""
    if not message:
        return
    if message.content.lower().startswith(('!add', '!delete')):
        #checks whether the message is just a command
        return
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    try:
        guild_id = message.guild.id
    except AttributeError:
        return
    #gets all the bad words from the guild's blacklist
    cursor.execute(f'SELECT word FROM badwords WHERE guild_id={guild_id}')
    swears = [swear[0] for swear in cursor.fetchall()]
    if not swears:
        return
    if bot.user == message.author:
        return
    for swearword in swears:
        #checks first whether the channel is NSFW(swearing is allowed there usually) then calls the is_substring function from my utils library that uses KMP for sake of complexity
        if not message.channel.is_nsfw() and is_substring(message.content.lower(), swearword):
            #deletes the message followed by a sending a message to the author
            await message.delete()
            await message.author.create_dm()
            await message.author.dm_channel.send(
                f'Hi {message.author}, you sent a message containing the following word: {swearword}'
            )
            return

#running the bot
bot.run(TOKEN)
