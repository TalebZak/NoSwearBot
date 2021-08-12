import os
from discord.ext import commands
from dotenv import load_dotenv
import discord
from utils.sweardetect import is_substring
from utils.DatabaseUtil import DatabaseUtil
import asyncio

intents = discord.Intents.all()
db = DatabaseUtil()
load_dotenv()
# Takes the bot's token that I have saved in a .env file and stores in the token variables
TOKEN = os.getenv('DISCORD_TOKEN')
# the commands are called by the command prefix '!', the fact that I made it case insensitive is for Discord mobile
# users
bot = commands.Bot(command_prefix='!', case_insensitive=True, intents=intents)


async def add_member(member, guild):
    if not db.exist_and("member", ["id"], (member.id,)):
        db.insert("member", (member.id, member.name, member.bot,))
        db.insert("membership", (member.id, guild.id))
    else:
        if not db.exist_and("membership", ["memberid", "guildid"], (member.id, guild.id)):
            db.insert("membership", (member.id, guild.id))


@bot.event
async def on_guild_join(guild):
    perms = discord.Permissions(send_messages=False, read_messages=True)
    await guild.create_role(name='NoSend', permissions=perms)
    if not db.exist_and("guild", ["id"], (guild.id,)):
        db.insert("guild", (guild.id, guild.name))
    for member in guild.members:
        await add_member(member, guild)


@bot.event
async def on_member_join(member):
    await add_member(member, member.guild)


@bot.event
async def on_member_remove(member):
    db.delete("membership", ["memberid", "guildid"], (member.id, member.guild.id))


async def kick(member, reason="breaking the swearing limit"):
    await member.kick(reason=reason)


@bot.commands(description='sets the limits of member swearing until they get kicked[default 3]',
              brief='sets the limits of member swearing')
@commands.has_permissions(administrator=True)
async def setlimit(ctx, limit=3):
    db.set("guild", ("limits",), ("guildid",), (limit,), (ctx.guild.id,))


async def punish(member, guild_id):
    current_infrigement = db.get("membership", ("infrigement",), ("memberid", "guildid"), (member.id, guild_id))[0][0]
    print(current_infrigement)
    time = db.get("guild", ("silencepenalty",), ("id",), (guild_id,))[0]
    db.set("membership", ("infrigement",), ("memberid", "guildid"), (current_infrigement + 1,), (member.id, guild_id))
    limit = db.get("guild", ("limits",), ("id",), (guild_id,))[0]
    if current_infrigement == limit:
        await member.dm_channel.send(f'You have misbehaved and you will be kicked from this server')
        await kick(member)
    else:
        await member.create_dm()
        await member.dm_channel.send(
            f'Hi {member}, you have {limit - current_infrigement} times left before getting kicked from this server'
        )


@bot.command(description='blacklists a word if it was not blacklisted already', brief='blacklists a word')
@commands.has_permissions(administrator=True)
async def add(ctx, word=None):
    """This function adds a word to the swears database
        Args:
            ctx: A context variables that refers to the channel, and other details that a command usually requires
            word: The new swear word that the Guild member wants to add to the blacklist(default is None in case a user
                  forgets)
        Returns:
            Doesn't have a return value"""
    if not word:
        await ctx.send('you are not adding anything')
        return
    # first connecting to the main database
    # getting the guild's id from the context to allow mapping
    guild_id = ctx.guild.id
    # searches if the word that a user wants to add to avoid duplicates
    try:
        db.insert("blacklist", (guild_id, word))
        await ctx.send(f'{word} was added to the blacklist')
    except Exception:
        await ctx.send('word already exists')


@bot.command(description='lists all the words that were blacklisted in the server', brief='lists all blacklisted words')
async def listwords(ctx):
    """A function that allows a guild member to see all the blacklisted words in the guild
       Args:
            ctx: Context variables required by the command to get details like guild id
       Returns:
            Doesn't have a return value"""

    guild_id = ctx.guild.id
    swears = db.get("blacklist", fields=("term",), conditions=("guildid",), values=(guild_id,))
    # a list comprehension since the fetchall method returns a tuple in the form of (word,)
    words = [swear[0] for swear in swears]
    if not words:
        await ctx.send('There are no blacklisted words')
        return
    # basic message formatting for the swearwords
    wordlist = ''.join([f'-{word}\n' for word in words])
    await ctx.send(f'the swearwords in this server are:\n{wordlist}')


@bot.command(description='allows the creator of the server to remove a word from the blacklist',
             brief='removes a blacklisted word')
@commands.has_permissions(administrator=True)
async def delete(ctx, word=None):
    """A command that allows the admin to delete swear words and make users able to say it for any reasons. Only the owner has that privilege for one simple
       reason which is avoid any sort of undesired deletion of word that can make others feel uncomfortable
       Args:
           ctx: Context variable for the command to see the guild and author
           word: the word to delete from the blacklist
       Returns:
            Doesn't have a return value"""
    """if ctx.author != ctx.guild.owner:
        # in case the author of the command is not the same person as the guild owner
        await ctx.send("Only the server owners are allowed to change the blacklist")
        return"""
    if not word:
        await ctx.send("Your command doesn't contain a word to delete")
        return
    guild_id = ctx.guild.id
    exists = db.exist_and("blacklist", ["term", "guildid"], (word, guild_id))
    if exists:
        db.delete("blacklist", ("guildid", "term"), (guild_id, word))
        await ctx.send(f'{word} was successfully deleted')

    else:
        # if the word does not exist already, this message is displayed
        await ctx.send(f'{word} is not blacklisted')


@bot.event
async def on_ready():
    # used for debugging purposes
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
    message.content = message.content.replace(' ', '')
    if message.content.lower().startswith(('!add', '!delete', '!listwords')):
        # checks whether the message is just a command
        return
    try:
        guild_id = message.guild.id
    except AttributeError:
        return

    # gets all the bad words from the guild's blacklist
    swears = [swear[0] for swear in db.get("blacklist", fields=("term",), conditions=("guildid",), values=(guild_id,))]
    if bot.user == message.author or message.author.bot:
        return
    for swearword in swears:
        # checks first whether the channel is NSFW(swearing is allowed there usually) then calls the is_substring
        # function from my utils library that uses KMP for complexity
        if not message.channel.is_nsfw() and is_substring(message.content.lower(), swearword):
            # deletes the message followed by a sending a message to the author
            await message.delete()
            await punish(message.author, guild_id)


# running the bot
bot.run(TOKEN)
