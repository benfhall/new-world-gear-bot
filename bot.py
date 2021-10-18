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
armor_types = ["light", "medium", "heavy"]
factions = ["covenant","marauder","syndicate"]
fac_color = { "covenant":0xf0c400, "marauder":0x16801d, "syndicate":0x8a10c7}

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
        color=fac_color.get(str(await database.pull_by_index(index, "faction")).lower(),0x000000)
    )
    embed.description = str(await database.pull_by_index(index, "company")).title()
    embed.add_field(name="IGN",value=str(await database.pull_by_index(index, "ign")).title())
    embed.add_field(name="Level",value=str(await database.pull_by_index(index, "level")).title())
    embed.add_field(name="Gear Score",value=str(await database.pull_by_index(index, "gs")).title())
    embed.add_field(name="Armor Weight",value=str(await database.pull_by_index(index, "armor")).title())
    embed.add_field(name="Primary Weapon",value=str(await database.pull_by_index(index, "primary")).title())
    embed.add_field(name="Secondary Weapon",value= str(await database.pull_by_index(index, "secondary")).title())

    embed.set_thumbnail(url=target.avatar_url)
    img_link = str(await database.pull_by_index(index, "img"))
    if validators.url(img_link):
        embed.set_image(url=img_link)

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
            return "n/a"
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
    await ctx.channel.send("If you make any errors, you can go back anytime after by doing `!update [field]`.\nThe field will be listed after the question around brackets, [field].")

    # update name
    await database.push(ctx.author.id, "name", ctx.author.name)

    if field == None or str(field) == "ign":
        res = await text_res(ctx.author,'```What is your in-game name? [ign]```')
        await database.push(ctx.author.id, "ign", res)

    # set faction
    if field == None or str(field) == "faction":
        res = await text_res(ctx.author,'```What faction are you in? (covenant/marauder/syndicate) [faction]```')
        if res.lower() in factions:
            await database.push(ctx.author.id, "faction", res)
        else:
            await ctx.author.send("Invalid response, skipping/aborting update.")

    # set company
    if field == None or str(field) == "company":
        res = await text_res(ctx.author,'```What is the name of your company in game? [company]```')
        await database.push(ctx.author.id, "company", res)

    # set lvl
    if field == None or str(field) == "lvl":
        res = await text_res(ctx.author,'```What level is your character currently in New World? [lvl]```')
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
        res = await text_res(ctx.author,'```What gear score is your character currently in New World? [gs]```')
        try:
            res = int(res)
            if res >= 1 and res <= 600:
                await database.push(ctx.author.id, "gs", res)
            else:
                raise ValueError
        except ValueError:
            await ctx.author.send("Invalid response, skipping/aborting update.")

    # set armor type
    if field == None or str(field) == "armor":
        res = str(await text_res(ctx.author,'```What is the weight of your armor? (i.e light, medium, heavy) [armor]```')).lower()
        if res in armor_types:
            await database.push(ctx.author.id, "armor", res)
        else:
            await ctx.author.send("Invalid response, skipping/aborting update.")

    # set primary
    if field == None or str(field) == "primary":
        res = str(await text_res(ctx.author,'```What is your primary weapon? (i.e fire staff, great axe, sword) [primary]```')).lower()
        if res in weapon_types:
            await database.push(ctx.author.id, "primary", res)
        else:
            await ctx.author.send("Invalid response, skipping/aborting update.")

    # set secondary
    if field == None or str(field) == "secondary":
        res = str(await text_res(ctx.author,'```What is your secondary weapon? (i.e fire staff, great axe, sword) [secondary]```')).lower()
        if res in weapon_types:
            await database.push(ctx.author.id, "secondary", res)
        else:
            await ctx.author.send("Invalid response, skipping/aborting update.")

    # set image
    if field == None or str(field) == "img":
        res = await text_res(ctx.author,'```Please provide a link to an image of your gear, showing attributes. (link) [img]```')
        if validators.url(res):
            await database.push(ctx.author.id, "img", res)
        else:
            await ctx.author.send("Invalid response, skipping/aborting update.")
    
    # set date
    today = date.today()
    await database.push(ctx.author.id, "date", str(today.strftime("%m/%d/%Y")))

    await ctx.author.send("Updating process complete!")

@bot.command(pass_context=True)
async def help(ctx):
    """prints user help info"""
    embed = discord.Embed(
        title="New World Gearbot Help",
        color=0xE51837
    )
    embed.set_thumbnail(url=bot.user.avatar_url)
    embed.add_field(name="Commands", value="Find the commands [here](https://github.com/Swidex/new-world-gear-bot#commands)")
    embed.add_field(name="Invite", value="Invite this bot [here](https://discord.com/api/oauth2/authorize?client_id=899228215204282380&permissions=347200&scope=bot)")
    await ctx.channel.send(embed=embed)

bot.run(DISCORD_TOKEN)