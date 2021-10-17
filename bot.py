import discord, os, asyncio, validators
from discord.ext import commands
from dotenv import load_dotenv
from database import Database
from datetime import date

# initialize discord connection and configuration
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix="!", help_command=None)

database = Database()
weapon_types = ["fire staff","ice gauntlet","life staff","bow","musket","sword","great axe","hatchet","hammer","spear","rapier"]

@bot.event
async def on_ready():
    """on connect handler"""
    print(f'{bot.user} has connected to Discord!')

@bot.command(pass_context=True)
async def gear(ctx, target: discord.User=None):
    """create embed with target's information"""
    # make target author if blank
    if target is None:
        target = ctx.author

    # return message if user not found
    try:
        index = await database.find_index(target.id)
    except ValueError:
        await ctx.channel.send("```" + target.name + " was not found in the gear database.```")

    # create return embed
    embed = discord.Embed(
        title=target.name + "'s Gear",
        color=0xE51837
    )
    embed.add_field(name="Level",value=str(await database.pull_by_index(index, "level")).title())
    embed.add_field(name="Gear Score",value=str(await database.pull_by_index(index, "gs")).title())
    embed.add_field(name = chr(173), value = chr(173)) # line break
    embed.add_field(name="Primary Weapon",value=str(await database.pull_by_index(index, "primary")).title())
    embed.add_field(name="Secondary Weapon",value=str(await database.pull_by_index(index, "secondary")).title())

    embed.set_image(url=str(await database.pull_by_index(index, "img")))
    embed.set_thumbnail(url=target.avatar_url)

    embed.set_footer(text="Last Updated: " + str(await database.pull_by_index(index, "date")))

    await ctx.channel.send(embed=embed)

async def text_res(member, question):
    try:
        await member.send(question)
    except discord.HTTPException:
        pass
    else: 
        try:
            msg = await bot.wait_for('message', check = lambda x: x.channel == member.dm_channel and x.author == member, timeout=60)
        except asyncio.TimeoutError:
            return ""
        finally:
            return msg.content

@bot.command(pass_context=True)
async def update(ctx, field=None):
    """update user information"""
    try:
        index = await database.find_index(ctx.author.id)
    except ValueError:
        field = None
        await ctx.author.send("Not found in database, running entire update process.")

    # update name
    await database.push(ctx.author.id, "name", ctx.author.name)

    # set lvl
    if field == None or str(field) == "lvl":
        res = await text_res(ctx.author,'```What level is your character currently in New World? (1-60)```')
        try:
            res = int(res)
            if res >= 1 and res <= 60:
                await database.push(ctx.author.id, "level", res)
            else:
                raise ValueError
        except ValueError:
            await ctx.author.send("Invalid response, skipping/aborting update.")

    # set gs
    if field == None or str(field) == "gs":
        res = await text_res(ctx.author,'```What gear score is your character currently in New World? (1-600)```')
        try:
            res = int(res)
            if res >= 1 and res <= 600:
                await database.push(ctx.author.id, "gs", res)
            else:
                raise ValueError
        except ValueError:
            await ctx.author.send("Invalid response, skipping/aborting update.")

    # set primary
    if field == None or str(field) == "primary":
        res = str(await text_res(ctx.author,'```What is your primary weapon? (i.e fire staff, great axe, sword)```')).lower()
        if res in weapon_types:
            await database.push(ctx.author.id, "primary", res)
        else:
            await ctx.author.send("Invalid response, skipping/aborting update.")

    # set secondary
    if field == None or str(field) == "secondary":
        res = str(await text_res(ctx.author,'```What is your secondary weapon? (i.e fire staff, great axe, sword)```')).lower()
        if res in weapon_types:
            await database.push(ctx.author.id, "secondary", res)
        else:
            await ctx.author.send("Invalid response, skipping/aborting update.")

    # set image
    if field == None or str(field) == "img":
        res = await text_res(ctx.author,'```Please provide a link to an image of your gear, showing attributes. (link)```')
        if validators.url(res):
            await database.push(ctx.author.id, "img", res)
        else:
            await ctx.author.send("Invalid response, skipping/aborting update.")
    
    # set date
    today = date.today()
    await database.push(ctx.author.id, "date", str(today.strftime("%m/%d/%Y")))

@bot.command(pass_context=True)
async def help(ctx):
    """prints user help info"""
    embed = discord.Embed(
        title="New World Gearbot Help",
        color=0xE51837
    )
    embed.set_thumbnail(url=bot.user.avatar_url)
    embed.add_field(name="Commands", value="Find the commands [here](https://github.com/Swidex/new-world-gear-bot)")
    embed.add_field(name="Invite", value="Invite this bot [here](https://discord.com/api/oauth2/authorize?client_id=899228215204282380&permissions=347200&scope=bot)")
    await ctx.channel.send(embed=embed)

bot.run(DISCORD_TOKEN)