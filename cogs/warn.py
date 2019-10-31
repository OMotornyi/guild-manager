from discord.ext import commands,tasks
import discord
from collections import defaultdict
from swgoh_db import db_query_player_id, db_update_player,db_create_connection,db_add_warn, db_query_all_players,db_player_in_guild
from swgoh_db import db_list_warn, db_dell_warn
from datetime import datetime


class WarnCog(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.count = 0
        self.seconds = 5
        self.minutes = 0
        self.hours = 0
        self.printer.start()

    @commands.group(case_insensitive=True)
    async def warn(self, ctx):
            if ctx.invoked_subcommand is None:
                await ctx.send('{0.subcommand_passed} is not a correct guild command'.format(ctx))  

    @warn.command(name="add")
    async def add_warn(self, ctx,allycode:int,*args):
        await ctx.send(allycode)
        await ctx.send(" ".join(args))
        await ctx.send("New warning") 
        database = "guild.db"
        conn = db_create_connection(database)
        with conn:
            if db_player_in_guild(conn,allycode):
                date = datetime.now().strftime("%d/%m/%Y")
                db_add_warn(conn,[allycode,date," ".join(args)])
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
                reply+=f"""\t{days_delta} ago ({w[0]}), {w[1]}\t id: {w[2]}\n"""
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

    @commands.command(name='repeat', aliases=['copy', 'mimic'])
    async def do_repeat(self, ctx, *, our_input: str):
        """A simple command which repeats our input.
        In rewrite Context is automatically passed to our commands as the first argument after self."""

        await ctx.send(our_input)

    @commands.command(name='add', aliases=['plus'])
    @commands.guild_only()
    async def do_addition(self, ctx, first: int, second: int):
        """A simple command which does addition on two integer values."""

        total = first + second
        await ctx.send(f'The sum of **{first}** and **{second}**  is  **{total}**')

    @commands.command(name='me')
    @commands.is_owner()
    async def only_me(self, ctx):
        """A simple command which only responds to the owner of the bot."""

        await ctx.send(f'Hello {ctx.author.mention}. This command can only be used by you!!')

    @commands.command(name='embeds')
    @commands.guild_only()
    async def example_embed(self, ctx):
        """A simple command which showcases the use of embeds.
        Have a play around and visit the Visualizer."""

        embed = discord.Embed(title='Example Embed',
                              description='Showcasing the use of Embeds...\nSee the visualizer for more info.',
                              colour=0x98FB98)
        embed.set_author(name='MysterialPy',
                         url='https://gist.github.com/MysterialPy/public',
                         icon_url='http://i.imgur.com/ko5A30P.png')
        embed.set_image(url='https://cdn.discordapp.com/attachments/84319995256905728/252292324967710721/embed.png')

        embed.add_field(name='Embed Visualizer', value='[Click Here!](https://leovoel.github.io/embed-visualizer/)')
        embed.add_field(name='Command Invoker', value=ctx.author.mention)
        embed.set_footer(text='Made in Python with discord.py@rewrite', icon_url='http://i.imgur.com/5BFecvA.png')

        await ctx.send(content='**A simple Embed for discord.py@rewrite in cogs.**', embed=embed)

    @tasks.loop(seconds=5)
    async def printer(self):
        self.count+=1
    @commands.command()
    async def counter(self,ctx):
        await ctx.send(self.count)
    @commands.command()
    async def increase_loop(self,ctx):
        self.minutes+=1
        self.printer.change_interval(minutes = self.minutes)
def setup(bot):
            bot.add_cog(WarnCog(bot))