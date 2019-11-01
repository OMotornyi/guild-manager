from discord.ext import commands,tasks
import discord
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
        self.printer.start()
        self.warn_cleanup.start()

    @commands.group(case_insensitive=True)
    async def warn(self, ctx):
            if ctx.invoked_subcommand is None:
                await ctx.send('{0.subcommand_passed} is not a correct guild command'.format(ctx))  

    @warn.command(name="add")
    async def add_warn(self, ctx,allycode:int,date_input:str,*, args):
        await ctx.send(allycode)
        await ctx.send(args)
        try:
            #date = datetime.strptime(date_input,"%d/%m/%Y")
            date = dateutil.parser.parse(date_input,dayfirst = True)
            date = date.strftime("%d/%m/%Y")
        except ValueError:
            args = date_input + args
            date = datetime.now().strftime("%d/%m/%Y")        
        #await ctx.send("New warning") 
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
                reply+=f"""\t{days_delta} days ago ({w[0]}), {w[1]}\t id: {w[2]}\n"""
        print(reply)
        reply = reply+"\n```"
        await ctx.send(reply)


    @warn.command(name="remove")
    async def remove_warn(self, ctx,id:int):
        database = "guild.db"
        conn = db_create_connection(database)
        print (type(id))
        with conn:
            db_dell_warn(conn,id)
        await ctx.send("Remove warning")

 
    @tasks.loop(seconds=5)
    async def printer(self):
        self.count+=1
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
    @commands.command()
    async def counter(self,ctx):
        await ctx.send(self.count)
    @commands.command()
    async def increase_loop(self,ctx):
        self.minutes+=1
        self.printer.change_interval(minutes = self.minutes)
def setup(bot):
            bot.add_cog(WarnCog(bot))