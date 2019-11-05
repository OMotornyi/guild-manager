import discord
from discord.ext import commands, tasks
import asyncio
import aiofiles
import aiohttp
#import shlex
import sys
import sqlite3
from sqlite3 import Error
#from swgoh_db import db_query_player_id, db_update_player,db_create_connection,db_add_warn, db_query_all_players,db_player_in_guild
#from swgoh_db import db_list_warn, db_dell_warn
#from collections import defaultdict
#import swgoh_db as swdb
#from swgoh_api import get_guild_full,get_guild_members, CONFIG
#from swgohhelp import CONFIG, fetch_guilds
from datetime import datetime

token = sys.argv[1]  # I've opted to just save my token to a text file. 


description = '''A simple discord bot with some SWGOH guild managment utilities'''
initial_extensions = ['cogs.warn','cogs.guild_players']
bot = commands.Bot(command_prefix='?', description=description, case_insensitive=True)

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')
    print('------')



# @bot.command()
# async def players(ctx,allycode: int):
#     guild_members=get_guild_members(CONFIG,allycode) 
#     print(guild_members)
#     print(guild_members.keys() )
#     guild_members_list = [  [x['name'],x['gp']] for x in guild_members[list(guild_members)[0]] ] 
#     reply="""```\n"""
#     for pl in guild_members_list:
#         reply=reply+pl[0]+"\n"
#         reply=reply+f"{pl[0]} has total GP of {pl[1]}"
#     reply = reply+"\n```"
#     await ctx.send(reply )

# @bot.group(case_insensitive=True)
# async def guild(ctx):
#         #await ctx.send(ctx.command)
#         #await ctx.send(ctx.message)
#         #await ctx.send(ctx.args)
#         #await ctx.send(f" the command was invoked with {ctx.invoked_with}")
#         #await ctx.send(f"and we passed a sub:{ctx.subcommand_passed}")
#         if ctx.invoked_subcommand is None:
#             await ctx.send('{0.subcommand_passed} is not a correct guild command'.format(ctx))

# @guild.command(name="list")
# async def _list(ctx,allycode: int,with_codes = '0'):
#     '''Prints all guild members from DB'''
#     from operator import itemgetter
#     database = "guild.db"
#     #if with_codes == "with": w
#     conn = db_create_connection(database)
#     with conn:
#         guild_members_list=db_query_all_players(conn)
#         #print("WTF")
#         #await ctx.send( guild_members_list)
#     #print(guild_members_list)
#    # guild_members_list=[ list(player).append(player[4]+player[5]) for player in guild_members_list]
#     for idx, player in enumerate(guild_members_list):
#         guild_members_list[idx]=list(player)
#         guild_members_list[idx].append(player[4]+player[5])
#     #print(guild_members_list)
#     guild_members_list.sort(key=itemgetter(6),reverse=True)
#     longest_name=max( map(len,[x[2] for x in guild_members_list]) ) 
#     reply="""```\n"""
#     allycodes = ""
#     for pl in guild_members_list:
#         #reply=reply+pl[0]+"\n"
#         if with_codes == "with": allycodes=f" ({pl[1]})"
#         reply_line = f"""{pl[2]}{allycodes} {(longest_name-len(pl[2]))*" "} {pl[6]/1000000:.2f}M \n"""
#         if len(reply+reply_line)>2000:
#             reply = reply+"\n```"
#             await ctx.send(reply)
#             reply="""```\n"""
#         else:
#             reply=reply+reply_line
#     reply = reply+"\n```"
# #    await ctx.send(len(reply))
#     await ctx.send(reply )
# #   await ctx.send("Command to print guild members list")

# @guild.command()
# async def update(ctx,allycode: int):
#     """Updated the list of guild members in DB """
#     from operator import itemgetter
#     database = "guild.db"
#     conn = db_create_connection(database)
#     guild_members=get_guild_full(CONFIG,allycode) 
#     guild_members_list = [  [x['allyCode'],x['name'],x['gpShip']+x['gpChar'],x['gpChar'],x['gpShip']] for x in guild_members[0]['roster'] ] 
#     guild_members_list.sort(key=itemgetter(3),reverse=True)
#     with conn:
#         for player in guild_members_list:
#             db_update_player(conn,(guild_members[0]['updated'],player[4],player[3],player[0],player[1]))
#             #print(id)
#     longest_name=max( map(len,[x[1] for x in guild_members_list]) )
#     await ctx.send(longest_name)
    
#     reply="""```\n"""
#     for pl in guild_members_list:
#         #reply=reply+pl[0]+"\n"
#         reply=reply+f"""{pl[1]} {(longest_name-len(pl[1]))*" "} {pl[2]/1000000:.2f}M \n"""
#     reply = reply+"\n```"
#     await ctx.send(len(reply))
#     #print(reply)
#     await ctx.send(reply)

@bot.command()
async def reload(ctx):
    for extension in initial_extensions:
        bot.reload_extension(extension)

@bot.command(aliases=['stop','exit'])
async def logout(ctx):
    """Logs out."""
    await bot.close()



bot.run(token)

def foo() -> int:
    return "foo"