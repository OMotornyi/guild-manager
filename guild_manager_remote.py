import discord
from discord.ext import commands
import asyncio
import aiofiles
import aiohttp
import shlex
import sys
import sqlite3
from sqlite3 import Error
from swgoh_db import db_query_player_id, db_update_player,db_create_connection,db_add_warn, db_query_all_players,db_player_in_guild
from swgoh_db import db_list_warn, db_dell_warn
from collections import defaultdict
#import swgoh_db as swdb
from swgoh_api import get_guild_full,get_guild_members, CONFIG
from datetime import datetime

token = sys.argv[1]  # I've opted to just save my token to a text file. 


description = '''An example bot to showcase the discord.ext.commands extension
module.
There are a number of utility commands being showcased here.'''
bot = commands.Bot(command_prefix='?', description=description, case_insensitive=True)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command()
async def players(ctx,allycode: int):
    guild_members=get_guild_members(CONFIG,allycode) 
    print(guild_members)
    print(guild_members.keys() )
    guild_members_list = [  [x['name'],x['gp']] for x in guild_members[list(guild_members)[0]] ] 
    reply="""```\n"""
    for pl in guild_members_list:
        reply=reply+pl[0]+"\n"
        reply=reply+f"{pl[0]} has total GP of {pl[1]}"
    reply = reply+"\n```"
    await ctx.send(reply )

@bot.group(case_insensitive=True)
async def guild(ctx):
        await ctx.send(ctx.command)
        #await ctx.send(ctx.message)
        await ctx.send(ctx.args)
        await ctx.send(f" the command was invoked with {ctx.invoked_with}")
        await ctx.send(f"and we passed a sub:{ctx.subcommand_passed}")
        if ctx.invoked_subcommand is None:
            await ctx.send('{0.subcommand_passed} is not a correct guild command'.format(ctx))

@guild.command(name="list")
async def _list(ctx,allycode: int):
    '''Prints all guild members from DB'''
    from operator import itemgetter
    database = "guild"
    conn = db_create_connection(database)
    with conn:
        guild_members_list=db_query_all_players(conn)
        print("WTF")
        #await ctx.send( guild_members_list)
    print(guild_members_list)
   # guild_members_list=[ list(player).append(player[4]+player[5]) for player in guild_members_list]
    for idx, player in enumerate(guild_members_list):
        guild_members_list[idx]=list(player)
        guild_members_list[idx].append(player[4]+player[5])
    #print(guild_members_list)
    guild_members_list.sort(key=itemgetter(6),reverse=True)
    longest_name=max( map(len,[x[2] for x in guild_members_list]) ) 
    reply="""```\n"""
    for pl in guild_members_list:
        #reply=reply+pl[0]+"\n"
        reply=reply+f"""{pl[2]} {(longest_name-len(pl[2]))*" "} {pl[6]/1000000:.2f}M \n"""
    reply = reply+"\n```"
#    await ctx.send(len(reply))
    await ctx.send(reply )
#   await ctx.send("Command to print guild members list")

@guild.command()
async def update(ctx,allycode: int):
    """Updated the list of guild members in DB """
    from operator import itemgetter
    database = "guild"
    conn = db_create_connection(database)
    guild_members=get_guild_full(CONFIG,allycode) 
    guild_members_list = [  [x['allyCode'],x['name'],x['gpShip']+x['gpChar'],x['gpChar'],x['gpShip']] for x in guild_members[0]['roster'] ] 
    guild_members_list.sort(key=itemgetter(3),reverse=True)
    with conn:
        for player in guild_members_list:
            db_update_player(conn,(guild_members[0]['updated'],player[4],player[3],player[0],player[1]))
            #print(id)
    longest_name=max( map(len,[x[1] for x in guild_members_list]) )
    await ctx.send(longest_name)
    
    reply="""```\n"""
    for pl in guild_members_list:
        #reply=reply+pl[0]+"\n"
        reply=reply+f"""{pl[1]} {(longest_name-len(pl[1]))*" "} {pl[2]/1000000:.2f}M \n"""
    reply = reply+"\n```"
    await ctx.send(len(reply))
    #print(reply)
    await ctx.send(reply )

@bot.group(case_insensitive=True)
async def warn(ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('{0.subcommand_passed} is not a correct guild command'.format(ctx))  

@warn.command(name="add")
async def add_warn(ctx,allycode:int,*args):
    await ctx.send(allycode)
    await ctx.send(" ".join(args))
    await ctx.send("New warning") 
    database = "guild"
    conn = db_create_connection(database)
    with conn:
        if db_player_in_guild(conn,allycode):
            date = datetime.now().strftime("%d/%m/%Y")
            db_add_warn(conn,[allycode,date," ".join(args)])
            await ctx.send("A strike has been added")
        else:
            await ctx.send("Error: player with this allycode is not in the guild. Did you boot him already?")

@warn.command(name="list")
async def list_warn(ctx):
    database = "guild"
    conn = db_create_connection(database)
    with conn:
        warnings = db_list_warn(conn)
    warn_formated=defaultdict(list)
    print(warnings)
    for w in warnings:
        warn_formated[tuple(w[:2])].append(w[2:])
    reply="""```md\n **LIST OF WARNINGS**\n"""
    for key,values in warn_formated.items():
        name_code=f"{key[0]} {key[1]}:\n"
        reply+=name_code
        for w in values:
            reply+=f"""\t{w[0]}, {w[1]}\t id: {w[2]}\n"""
    print(reply)
    reply = reply+"\n```"
    await ctx.send(reply)


@warn.command(name="remove")
async def remove_warn(ctx,id:int):
    database = "guild"
    conn = db_create_connection(database)
    print (type(id))
    with conn:
        db_dell_warn(conn,id)
    await ctx.send("Remove warning")




@bot.command(aliases=['stop','exit'])
async def logout(ctx):
    """Logs out."""
    await bot.close()



bot.run(token)
