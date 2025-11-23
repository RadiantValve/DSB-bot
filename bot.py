from dsb import DSBPlanExtractor
from dotenv import load_dotenv
import discord
import time
import os

load_dotenv(dotenv_path='DSB-bot/.env')
DSB_ID = os.getenv('ID')
DSB_USER = os.getenv('USERNAME')
TOKEN = os.getenv('DISCORD_TOKEN')
print(TOKEN)

Intents = discord.Intents.default()
# dm intents
Intents.dm_messages = True
Intents.dm_reactions = True
Intents.dm_typing = True
#server intents
Intents.guild_messages = True
Intents.guild_reactions = True
Intents.guild_typing = True
Intents.guilds = True
Intents.members = True

client = discord.Client(intents=Intents)

@client.event
async def on_ready():
    print(client.user)
    for i in client.guilds:
        print(f'{i}\n{i.member_count}')
        for o in i.members:
            print(o)

@client.event
async def on_message(message):
    print(message)
    print(message.author)
    print(message.content)

    if message.author == client.user:
        return
    
    if message.content.startswith("get"):
        file_list = []
        await message.channel.send("ok")
        extractor = DSBPlanExtractor(DSB_ID, DSB_USER)
        extractor.get_all()

        for root, dirs, files in os.walk(os.getcwd()):
            for file in files:
                if file.endswith('.jpg'):
                    file_list.append(file)
                    await message.channel.send(file=discord.File(f'images/{file}'))
        print(file_list)
    
    else:
        await message.channel.send("Hallo!")
    time.sleep(5)


client.run(TOKEN)