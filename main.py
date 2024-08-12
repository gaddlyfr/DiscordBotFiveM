import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
import dataRecover
import datetime
import pytz

intents = discord.Intents.all()
client = commands.Bot(command_prefix='$', intents=intents)
client.remove_command("help")

areas = {}


@client.event
async def on_ready():
    global areas
    print("Ready!")
    areas = dataRecover.recover_data()
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="$help"))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    earnings = 4000000

    if message.channel.id == 1271184354244296846:
        if message.embeds:
            for embed in message.embeds:
                footer_text = embed.footer.text
                if "Sun" in footer_text or "Sat" in footer_text:
                    earnings += 4000000

                userId = (embed.description.split("<")[1]).split(">")[0][1:]

                if userId in areas:
                    areas[userId] += earnings
                else:
                    areas[userId] = earnings
                dataRecover.save_data(areas)
        else:
            await message.reply("rozjebancu")
    await client.process_commands(message)


@client.command()
async def strefy(ctx):
    embed = discord.Embed(title="Zarobki ze stref", color=discord.Color.red())

    if areas:
        for user_id, count in areas.items():
            user = ctx.guild.get_member(user_id) or await client.fetch_user(user_id)
            user_name = user.name if user else "?"
            embed.add_field(name=user_name, value=f"Ma na koncie {count / 1000000} Milionów $", inline=False)

    else:
        embed.description = "Nikt jeszcze nie przejal strefy"

    await ctx.send(embed=embed)


@client.command()
@has_permissions(administrator=True)
async def subtract(ctx, args: int, member: discord.Member):
    if str(member.id) in areas:
        areas[str(member.id)] -= int(args)
    else:
        areas[str(member.id)] = 0 - int(args)
    dataRecover.save_data(areas)
    await ctx.send(f"Odjeto {int(args) / 1000000} Milionow $ od {member}")


@client.command()
@has_permissions(administrator=True)
async def add(ctx, args: int, member: discord.Member):
    if str(member.id) in areas:
        areas[str(member.id)] += int(args)
    else:
        areas[str(member.id)] = int(args)
    dataRecover.save_data(areas)
    await ctx.send(f"Dodano {int(args) / 1000000} Milionow $ dla {member}")


@client.command()
async def help(ctx):
    embed = discord.Embed(title="Pomoc", color=discord.Color.brand_green())
    embed.add_field(name="Administracja:",
                    value="""$subtract (ilosc) (gracz) - Zmniejsza pieniadze dla gracza\n
                             $add (ilosc) (gracz) - Dodaje pieniadze dla gracza""",
                    inline=False)
    embed.add_field(name="Komendy podstawowe:",
                    value="""$strefy - Pokazuje stan konta pieniedzy przez strefy\n
                             $help - Pokazuje komendy\n
                             $zone (gracz/e) - Rozdzielenie za strefe""",
                    inline=False)

    await ctx.send(embed=embed)

@client.command()
async def zone(ctx, *args: discord.Member):
    timezone = pytz.timezone("Europe/Warsaw")
    time = datetime.datetime.now(timezone)

    earnings = 4000000
    if time.weekday() >= 5:
        earnings *= 2

    amount = len(args) + 1
    per_money = earnings / amount
    areas[str(ctx.message.author.id)] -= per_money * (amount - 1)
    for member in args:
        if str(member.id) in areas:
            areas[str(member.id)] += per_money
        else:
            areas[str(member.id)] = per_money

@client.command()
async def reset(ctx, *args: discord.Member):
    for member in args:
        areas[str(member.id)] = 0

client.run('')
