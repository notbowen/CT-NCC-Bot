from __future__ import print_function
import discord
import json
from discord.ext import commands
import os
from keep_alive import keep_alive
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2 import service_account
import asyncio
import random
import requests

#form options
with open("forms.txt", 'r')as f:
  forms = f.readlines()
  f.close()

#admin ids
with open('admins.txt', 'r')as f:
  admins = f.readlines()
  f.close()

#cast all ids into int
admins = [int(x) for x in admins]


#bot init and prefixes
def get_prefix(client, ctx):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    return prefixes[str(ctx.guild.id)]


intents = discord.Intents.all()
client = commands.Bot(command_prefix=get_prefix, intents=intents)
client.remove_command('help')


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online,
                                 activity=discord.Game('ncc help'))
    print('Bot is ready')


@client.event
async def on_guild_join(guild):
    with open('prefixes.json', 'r') as f:
        prefix = json.load(f)

    prefix[str(guild.id)] = 'ncc '

    with open('prefixes.json', 'w') as f:
        json.dump(prefix, f, indent=4)


@client.event
async def on_guild_remove(guild):
    with open('prefixes.json', 'r') as f:
        prefix = json.load(f)

    prefix.pop(str(guild.id))


#google form api thingy
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds = None
creds = service_account.Credentials.from_service_account_file('keys.json',
                                                              scopes=SCOPES)


#commands and stuff
@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! Latency: **{round(client.latency * 1000)}**ms')


@client.command()
async def help(ctx):
    embed = discord.Embed(title="Help", color=0x00ffb7)
    embed.set_thumbnail(
        url=
        "https://cdn.discordapp.com/attachments/861967320541167616/862283229755342848/220px-Ncadetclogo.png"
    )
    embed.set_footer(text=f"Requested by: {ctx.message.author.name}",
                     icon_url=f"{ctx.message.author.avatar_url}")
    embed.add_field(name="ping:",
                    value="Returns the latency of the bot.",
                    inline=False)
    embed.add_field(
        name="adminHelp: ",
        value=
        "Gets admin commands lmao.",
        inline=False)
    embed.add_field(name="source",
                    value="Sends source code link",
                    inline=False)
    embed.add_field(name="website",
                    value="Sends website of bot thingy",
                    inline=False)
    embed.add_field(name="suggest {suggestion}",
                    value="Sends a suggestion to jason lmao",
                    inline=False)
    await ctx.send(embed=embed)


@client.command()
async def adminHelp(ctx):
    embed = discord.Embed(title="Admin Help", color=0xffc421)
    embed.set_thumbnail(
        url=
        "https://cdn.discordapp.com/attachments/861967320541167616/862283229755342848/220px-Ncadetclogo.png"
    )
    embed.set_footer(text=f"Requested by: {ctx.message.author.name}",
                     icon_url=f"{ctx.message.author.avatar_url}")
    embed.add_field(name="ping:",
                    value="Returns the latency of the bot.",
                    inline=False)
    embed.add_field(
        name="consolidate: ",value="Consolidates stuff lmao.", inline=False)


@client.command()
async def consolidate(ctx, id=None):

    #validates roles
    user = ctx.author
    role = discord.utils.find(lambda r: r.name == 'NCC Experience Team',
                              ctx.message.guild.roles)
    if role not in user.roles:
        role = discord.utils.find(lambda r: r.name == 'NCC Planning Team',
                                  ctx.message.guild.roles)
        if role not in user.roles:
            await ctx.send(
                ':x: You cannot run this command, you need to be either <@&861965386919575584> or <@&861965299372392448> to run this command lmao'
            )
            return

    embed = discord.Embed(title="Form Options", color=0xffac05)
    embed.set_thumbnail(
        url=
        "https://cdn.discordapp.com/attachments/861967320541167616/862283229755342848/220px-Ncadetclogo.png"
    )
    embed.set_footer(text=f"Requested by: {ctx.message.author.name}",
                     icon_url=f"{ctx.message.author.avatar_url}")

    for i in forms:
        data = i.split(':')
        embed.add_field(name=f"{data[0]} - " + data[1],
                        value=f'Form Id: {data[2]}',
                        inline=False)
    reaction = await ctx.send(embed=embed)
    for i in forms:
        emoji = i.split(':')[0]
        await reaction.add_reaction(emoji)

    def check(reaction, user):
        return user == ctx.message.author

    try:
        reaction, user = await client.wait_for('reaction_add',
                                               timeout=60.0,
                                               check=check)
    except asyncio.TimeoutError:
        await ctx.send(':x:Timed out lmao')
    else:
        for i in forms:
            if str(reaction.emoji) == i.split(':')[0]:
                await getconsolidatethingy(ctx, id=i.split(':')[2])

@client.command()
async def source(ctx):
    await ctx.send('https://github.com/wHo69/CT-NCC-Bot')


@client.command()
async def website(ctx):
    await ctx.send('https://CT-NCC-Bot.hubowen.repl.co')

@client.command()
async def suggest(ctx, *,suggestion):
  with open("suggestions.json", "r")as f:
    data = json.load(f)
    f.close()
  
  #add a new dict to list
  dic = {
        "id": int(data[-1]["id"]) + 1,
        "user": str(ctx.author), 
        "suggestion": suggestion, 
        "status": "pending"
        }
  data.append(dic)

  with open("suggestions.json", "w")as f:
    json.dump(data, f)

  await ctx.send(":white_check_mark: Your suggestion has been sent :)")

@client.command()
async def suggestions(ctx):
  if ctx.author.id not in admins:
    await ctx.send(":x: You must be a bot admin to use this command >:)")
    return

  with open('suggestions.json', 'r')as f:
    data = json.load(f)
    f.close()
  
  pending = []
  for i in data:
    if i["status"] == "pending":
      pending.append(i)

  embed = discord.Embed(title="Pending Suggestions", color=0xffac05)
  embed.set_thumbnail(
      url=
      "https://cdn.discordapp.com/attachments/861967320541167616/862283229755342848/220px-Ncadetclogo.png"
  )
  embed.set_footer(text=f"Requested by: {ctx.message.author.name}",
                    icon_url=f"{ctx.message.author.avatar_url}")
  for i in pending:
    embed.add_field(name=f"Suggestion {i['id']} by {i['user']}",
                          value=f'Suggestion: {i["suggestion"]}',
                          inline=False)

  await ctx.send(embed=embed)

#suggestion accept/decline
@client.command()
async def decline(ctx, id=None, reason=None):
  if ctx.author.id not in admins: 
    await ctx.send(":x: You need to be a bot admin lmao")
    return

  if id==None: 
    await ctx.send(":x: You need a id u ding dong.")
    return

  #cast id into an integer
  id = int(id)

  with open("suggestions.json", "r")as f:
    data = json.load(f)
    f.close()

  data[id].update({"status": "declined"})

  with open("suggestions.json", "w")as f:
    json.dump(data, f, indent=4)
    f.close()

  if reason == None: reason = "None"

  #send to le suggestions channel
  channel = client.get_channel(869515138221371452)
  embed = discord.Embed(title=f"Suggestion by: {data[id]['user']} was declined", color=0xFF0000)
  embed.set_thumbnail(
      url=
      "https://cdn.discordapp.com/attachments/861967320541167616/862283229755342848/220px-Ncadetclogo.png"
  )
  embed.add_field(
                name=f"Suggestion: {data[id]['suggestion']}",
                value=f"Reason: {reason}", 
                inline=False)
  await channel.send(embed=embed)

@client.command()
async def accept(ctx, id=None, reason=None):
  if ctx.author.id not in admins: 
    await ctx.send(":x: You need to be a bot admin lmao")
    return

  if id==None: 
    await ctx.send(":x: You need a id u ding dong.")
    return

  #cast id into an integer
  id = int(id)

  with open("suggestions.json", "r")as f:
    data = json.load(f)
    f.close()

  data[id].update({"status": "accepted"})

  with open("suggestions.json", "w")as f:
    json.dump(data, f, indent=4)
    f.close()

  #send to le suggestions channel
  if reason == None:
    channel = client.get_channel(869515138221371452)
    embed = discord.Embed(title=f"Suggestion by: {data[id]['user']} was accepted", color=0x37e666)
    embed.set_thumbnail(
        url=
        "https://cdn.discordapp.com/attachments/861967320541167616/862283229755342848/220px-Ncadetclogo.png"
    )
    embed.add_field(
                  name=f"Suggestion: ",
                  value=f"{data[id]['suggestion']}", 
                  inline=False)
    await channel.send(embed=embed)
  else:
    channel = client.get_channel(869515138221371452)
    embed = discord.Embed(title=f"Suggestion by: {data[id]['user']} was accepted", color=0x37e666)
    embed.set_thumbnail(
        url=
        "https://cdn.discordapp.com/attachments/861967320541167616/862283229755342848/220px-Ncadetclogo.png"
    )
    embed.add_field(
                  name=f"Suggestion: {data[id]['suggestion']}",
                  value=f"Remarks: {reason}", 
                  inline=False)
    await channel.send(embed=embed)

@client.command(aliases = ['accepted'])
async def acceptedResponses(ctx):
  if ctx.author.id not in admins: 
    await ctx.send(":x: You need to be a bot admin lmao")
    return

  with open('suggestions.json', 'r')as f:
    data = json.load(f)
    f.close()

  accepted = []
  for i in data:
    if i["status"] == "accepted":
      accepted.append(i)

  embed = discord.Embed(title="Accepted Suggestions", color=0x69fa64)
  embed.set_thumbnail(
      url=
      "https://cdn.discordapp.com/attachments/861967320541167616/862283229755342848/220px-Ncadetclogo.png"
  )
  embed.set_footer(text=f"Requested by: {ctx.message.author.name}",
                    icon_url=f"{ctx.message.author.avatar_url}")
  for i in accepted:
    embed.add_field(name=f"Suggestion {i['id']} by {i['user']}",
                          value=f'Suggestion: {i["suggestion"]}',
                          inline=False)

  await ctx.send(embed=embed)

@client.command(aliases=['appendform'])
async def appendForm(ctx, emoji=None, name=None, id=None):
  global forms
  if ctx.author.id not in admins:
    await ctx.send(':x: You gotta have admin >:)')
    return

  if emoji == None or name == None or id == None:
    await ctx.send(':x: Wrong format, needs to be {emoji} {name} {id}')
    return

  forms.append(f'{emoji}:{name}:{id}')

  with open('forms.txt', 'w')as f:
    f.write('\n'.join(forms))
    f.close()
  
  await ctx.send(':white_check_mark: Added!')

@client.command()
async def faq(ctx):
    randomColor = lambda: random.randint(0,255)
    color = int("0x%02X%02X%02X" % (randomColor(),randomColor(),randomColor()), 16)
    embed=discord.Embed(title="Frequently Asked Questions", color=color)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/861967320541167616/862283229755342848/220px-Ncadetclogo.png")
    embed.add_field(name="1. When are our CCA sessions held?", value="Every Monday and Wednesday.", inline=False)
    embed.add_field(name="2. Is NCC tiring?", value="Each CCA session usually feels like a light to moderate workout :D", inline=False)
    embed.add_field(name="3. What do we do during NCC?", value="A variety of things. Mainly drills, Physical Training, games etc. More info can be found on our website at: https://sites.google.com/ctss.edu.sg/ct-ncc/training-schedule-and-events", inline=False)

    await ctx.send(embed=embed)

# Update training data command
@client.command()
async def updateTrainingInfo(ctx):
    # Gather data
    await ctx.send("Enter attire: ")

    try:
        attire = await client.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60.0)
    except asyncio.TimeoutError:
        await ctx.send(":x:Timed out")
        return

    await ctx.send("Enter venue: ")

    try:
        venue = await client.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60.0)
    except asyncio.TimeoutError:
        await ctx.send(":x:Timed out")
        return
    
    await ctx.send("Enter time to fall in: ")

    try:
        timing = await client.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60.0)
    except asyncio.TimeoutError:
        await ctx.send(":x:Timed out")
        return

    # Check if all data exists and save to dict
    if attire and venue and timing:
        data = {
            "attire": attire,
            "venue": venue,
            "timing": timing
        }

        data = str(data)
    else:
        await ctx.send(":x: Something went wrong (Data missing)")
        return

    # Save data to github
    req = requests.put(
            "https://api.github.com/repos/wHo69/CT-NCC-Bot/contents/training_data.json",
            headers={"Accept": "application/vnd.github.v3+json"},
            data={"message": "Update training data", "content": data}
            )


#async functions
async def getconsolidatethingy(ctx, id):
    # The ID and range of a sample spreadsheet.
    #SPREADSHEET_ID = '1cxu6npO2c_5ga_cVqsAbuETIxf894ALdEY5vXWuXeRE'
    #RANGE = 'Form Responses 1!A1:K'

    SPREADSHEET_ID = id
    RANGE = "A1:Z"

    try:
        service = build('sheets', 'v4', credentials=creds)
    except Exception as e:
        await ctx.send(f":x: Error: ```{e}```")
        return

    # Call the Sheets API
    sheet = service.spreadsheets()
    try:
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=RANGE,
                                    majorDimension="COLUMNS").execute()
    except Exception as e:
        await ctx.send(f":x: Error: ```{e}```")
        return
    values = result.get('values', [])

    names = [i.split('@')[0].replace('_', ' ') for i in values[1]]

    for i in values:
        if values.index(i) <= 2: continue
        index = 0
        embed = discord.Embed(title=i[0], color=0x00ffb7)
        embed.set_thumbnail(
            url=
            "https://cdn.discordapp.com/attachments/861967320541167616/862283229755342848/220px-Ncadetclogo.png"
        )
        embed.set_footer(text=f"Requested by: {ctx.message.author.name}",
                         icon_url=f"{ctx.message.author.avatar_url}")
        for j in i:
            if j == i[0]:
                pass
            else:
                if j == '': j = 'No Response Found'
                embed.add_field(name=names[index].title(), value=j, inline=False)
            index += 1
        await ctx.send(embed=embed)


#random connec stuff
keep_alive()
load_dotenv()
client.run(os.getenv('DISCORD_TOKEN'))

#misc
'''{
  "type": "service_account",
  "project_id": "ct-ncc-bot",
  "private_key_id": os.getenv('PRIVATE_KEY_ID'),
  "private_key": os.getenv('PRIVATE_KEY'),
  "client_email": os.getenv('CLIENT_EMAIL'),
  "client_id": os.getenv('CLIENT_ID'),
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": os.getenv('client_x509_cert_url')
}'''