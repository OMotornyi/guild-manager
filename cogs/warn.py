from discord.ext import commands,tasks
import discord
import asyncio
from collections import defaultdict
from swgoh_db import db_query_player_id, db_update_player,db_create_connection,db_add_warn, db_query_all_players,db_player_in_guild
from swgoh_db import db_list_warn, db_dell_warn
from datetime import datetime
import dateutil.parser


class WarnCog(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.count = 0
        self.seconds = 5
        self.minutes = 0
        self.hours = 0
        self.warn_cleanup.start()

    @commands.group(case_insensitive=True)
    async def warn(self, ctx):
        '''A set of commands for giving guild players strikes for missing 600 or anything else.'''
        if ctx.invoked_subcommand is None:
            await ctx.send('{0.subcommand_passed} is not a correct guild command'.format(ctx))  

    @warn.command(name="add")
    async def add_warn(self, ctx,allycode:int,date_input:str,*, args):
        '''Adds a warning for the player with given allycode and a reason.
        Optional: if you want a waring with an older date input it after the player allycode.
        Example: "?warn add 928428534 stop lossbering FFS!" to add warning for today or
        "?warn add 928428534 10/09 stop lossbering FFS!" to add warning for 10th September. '''
        #await ctx.send(allycode)
        #await ctx.send(args)
        try:
            #date = datetime.strptime(date_input,"%d/%m/%Y")
            date = dateutil.parser.parse(date_input,dayfirst = True)
            date = date.strftime("%d/%m/%Y")
        except ValueError:
            args = date_input +" " + args
            date = datetime.now().strftime("%d/%m/%Y")        
        #await ctx.send("New warning") 
       # warn_content = f"Do you want to add a following warning: 'allycode': {allycode}, 'date': {date}, 'reason': {args}"
        embed = discord.Embed(title='',
                              description="Do you want to add a following warning:",
                              colour=0x98FB98)

        embed.add_field(name='Allycode', value=allycode)
        embed.add_field(name='Date', value=date)
        embed.add_field(name='Reason', value=args)
        embed.add_field(name='Command Invoker', value=ctx.author.mention)
#        embed.set_footer(text='Made in Python with discord.py@rewrite', icon_url='http://i.imgur.com/5BFecvA.png')
        msg = await ctx.send( embed=embed)
        await msg.add_reaction("\u2705")
        #await msg.add_reaction("\u274E")
        await msg.add_reaction("\u274C")
        def check(reaction, user):
            return user == ctx.author and (str(reaction.emoji) == "\u2705" or str(reaction.emoji) =="\u274C")
        #msg = await ctx.send()

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=120.0, check=check)
        except asyncio.TimeoutError:
            await msg.delete()
        else:
            #await ctx.send('👍')
            #await msg.delete()
            if str(reaction.emoji) =="\u274C":
                await msg.delete()
            elif str(reaction.emoji) == "\u2705":

                database = "guild.db"
                conn = db_create_connection(database)
                with conn:
                    if db_player_in_guild(conn,allycode):
                        #date = datetime.now().strftime("%d/%m/%Y")
                        db_add_warn(conn,[allycode,date,args])
                        await ctx.send("A strike has been added")
                    else:
                        await ctx.send("Error: player with this allycode is not in the guild. Did you boot him already?")

    @add_warn.error
    async def add_warn_error(self, ctx,error):
        print(type(error))
        print(dir(error))
        await ctx.send(error)
        if isinstance(error, commands.BadArgument):
            print(type(error))
            print(error)
            await ctx.send(error)
            await ctx.send('I could not find that member...')

    @warn.command(name="list")
    async def list_warn(self, ctx):
        '''Lists all warnings from the database. No parameters'''
        database = "guild.db"
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
                days_delta = (datetime.now()-datetime.strptime(w[0],"%d/%m/%Y")).days
                reply+=f"""\t{days_delta} day(s) ago ({w[0]}), {w[1]}\t id: {w[2]}\n"""
        print(reply)
        reply = reply+"\n```"
        await ctx.send(reply)


    @warn.command(name="remove")
    async def remove_warn(self, ctx,id:int):
        '''Removes a warning with a given id (look up the id through the "warn list" command) '''
        database = "guild.db"
        conn = db_create_connection(database)
        print (type(id))
        with conn:
            db_dell_warn(conn,id)
        await ctx.send("Remove warning")

    @tasks.loop(hours=24)
    async def warn_cleanup(self):
        database = "guild.db"
        conn = db_create_connection(database)
        with conn:
            warnings = db_list_warn(conn)
            for w in warnings:
                days_delta = (datetime.now()-datetime.strptime(w[2],"%d/%m/%Y")).days
                if days_delta>60:
                    db_dell_warn(conn,w[4]) 
                    print(f"warning removed:{w}")
#    @commands.command()
#    async def increase_loop(self,ctx):
#        self.warn_cleanup.change_interval(hours = 24)

def setup(bot):
            bot.add_cog(WarnCog(bot))