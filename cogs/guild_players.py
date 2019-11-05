from discord.ext import commands,tasks
import discord
from collections import defaultdict
import sqlite3
import asyncio
from sqlite3 import Error
from swgoh_db import db_query_player_id, db_update_player,db_create_connection,db_add_warn, db_query_all_players,db_player_in_guild
from swgoh_db import db_list_warn, db_dell_warn, db_search_all_players
from collections import defaultdict
#import swgoh_db as swdb
#from swgoh_api import get_guild_full,get_guild_members, CONFIG
from swgohhelp import CONFIG, fetch_guilds
from datetime import datetime


class PlayersCog(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    # @commands.command()
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

    @commands.group(case_insensitive=True)
    async def guild(self, ctx):
        '''Set of commands to interact with the whole guild'''
        if ctx.invoked_subcommand is None:
                msg = await ctx.send('{0.subcommand_passed} is not a correct guild command'.format(ctx))
                #await msg.add_reaction("✅")
                await msg.add_reaction("\u2705")
                #await msg.add_reaction("\u274E")
                await msg.add_reaction("\u274C")
                def check(reaction, user):
                    return user == ctx.author and str(reaction.emoji) == "\u2705"

                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
                except asyncio.TimeoutError:
                    await ctx.send('👎')
                else:
                    await ctx.send('👍')
                    await msg.delete()

    @guild.command(name="list")
    async def _list(self, ctx,allycode: int,with_codes = '0'):
        '''Prints all guild members from DB. Provide an allycode of a guild member. Optional: if you want 
        it to display an allycode for each player after the name follow with "with"'''
        from operator import itemgetter
        database = "guild.db"
        #if with_codes == "with": w
        conn = db_create_connection(database)
        with conn:
            guild_members_list=db_query_all_players(conn)
            #print("WTF")
            #await ctx.send( guild_members_list)
        #print(guild_members_list)
    # guild_members_list=[ list(player).append(player[4]+player[5]) for player in guild_members_list]
        for idx, player in enumerate(guild_members_list):
            guild_members_list[idx]=list(player)
            guild_members_list[idx].append(player[4]+player[5])
        #print(guild_members_list)
        guild_members_list.sort(key=itemgetter(6),reverse=True)
        longest_name=max( map(len,[x[2] for x in guild_members_list]) ) 
        reply="""```\n"""
        allycodes = ""
        for pl in guild_members_list:
            #reply=reply+pl[0]+"\n"
            if with_codes == "with": allycodes=f" ({pl[1]})"
            reply_line = f"""{pl[2]}{allycodes} {(longest_name-len(pl[2]))*" "} {pl[6]/1000000:.2f}M \n"""
            if len(reply+reply_line)>2000:
                reply = reply+"\n```"
                await ctx.send(reply)
                reply="""```\n"""+reply_line
            else:
                reply=reply+reply_line
        reply = reply+"\n```"
    #    await ctx.send(len(reply))
        await ctx.send(reply )
    #   await ctx.send("Command to print guild members list")

    @guild.command(name="search")
    async def _search(self, ctx,name):
        '''Prints all guild members from DB. Provide an allycode of a guild member. Optional: if you want 
        it to display an allycode for each player after the name follow with "with"'''
        from operator import itemgetter
        database = "guild.db"
        #if with_codes == "with": w
        conn = db_create_connection(database)
        with conn:
            guild_members_list=db_search_all_players(conn,name)
            #print("WTF")
            #await ctx.send( guild_members_list)
        #print(guild_members_list)
    # guild_members_list=[ list(player).append(player[4]+player[5]) for player in guild_members_list]
        for idx, player in enumerate(guild_members_list):
            guild_members_list[idx]=list(player)
            guild_members_list[idx].append(player[4]+player[5])
        #print(guild_members_list)
        guild_members_list.sort(key=itemgetter(6),reverse=True)
        longest_name=max( map(len,[x[2] for x in guild_members_list]) ) 
        reply="""```\n"""
        allycodes = ""
        for pl in guild_members_list:
            #reply=reply+pl[0]+"\n"
            allycodes=f" ({pl[1]})"
            reply_line = f"""{pl[2]}{allycodes} {(longest_name-len(pl[2]))*" "} {pl[6]/1000000:.2f}M \n"""
            if len(reply+reply_line)>2000:
                reply = reply+"\n```"
                await ctx.send(reply)
                reply="""```\n"""+reply_line
            else:
                reply=reply+reply_line
        reply = reply+"\n```"
    #    await ctx.send(len(reply))
        await ctx.send(reply )
    #   await ctx.send("Command to print guild members list")



    @guild.command()
    async def update(self, ctx,allycode: int):
        """Updated the list of guild members in DB """
        from operator import itemgetter
        database = "guild.db"
        conn = db_create_connection(database)
        guild_members=await fetch_guilds(CONFIG,[allycode]) 
        guild_members_list = [  [x['allyCode'],x['name'],x['gpShip']+x['gpChar'],x['gpChar'],x['gpShip']] for x in guild_members[0]['roster'] ] 
        guild_members_list.sort(key=itemgetter(3),reverse=True)
        with conn:
            for player in guild_members_list:
                db_update_player(conn,(guild_members[0]['updated'],player[4],player[3],player[1],player[0]))
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
        await ctx.send(reply)

def setup(bot):
            bot.add_cog(PlayersCog(bot))