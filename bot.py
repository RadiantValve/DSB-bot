from dsb import DSBPlanExtractor
from dotenv import load_dotenv
from datetime import datetime
import discord
import shutil
import time
import os

load_dotenv(dotenv_path=f'/.env')
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
    
        # Look specifically for images in the 'images' folder
        images_folder = "images"
        if not os.path.exists(images_folder):
            await message.channel.send("The 'images' folder does not exist.")
            return
        
        for file in os.listdir(images_folder):
            if file.endswith('.jpg'):
                file_list.append(file)
                await message.channel.send(file=discord.File(os.path.join(images_folder, file)))
                time.sleep(.4)
        
        print(file_list)
        if file_list:
            await message.channel.send("done")
        else:
            await message.channel.send("No images found in the 'images' folder.")
        return
    
    if message.content.startswith("backup"):
        await message.channel.send("Starting backup...")
        
        backup_folder = "backup"
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)
        
        # Move images to the backup folder, organizing by date
        for file in os.listdir("images"):
            if file.endswith(".jpg"):
                # Extract the date from the filename (assuming format like 'subst_8b_2025-11-24.jpg')
                try:
                    # Split the filename and extract the date part
                    date_str = file.split("_")[-1].split(".")[0]  # Extract '2025-11-24'
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    date_folder = os.path.join(backup_folder, date_obj.strftime("%Y-%m-%d"))
                    
                    # Create the date folder if it doesn't exist
                    if not os.path.exists(date_folder):
                        os.makedirs(date_folder)
                    
                    # Move the file to the date folder
                    shutil.move(os.path.join("images", file), os.path.join(date_folder, file))
                except ValueError:
                    await message.channel.send(f"Skipping file with invalid date format: {file}")
        
        await message.channel.send("Backup completed!")
    
    else:
        await message.channel.send("Hallo!")
    time.sleep(5)


client.run(TOKEN)